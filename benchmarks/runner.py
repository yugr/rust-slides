#!/usr/bin/env python3

import argparse
import glob
import os
import os.path
from pathlib import Path
import subprocess
import sys

me = os.path.basename(__file__)

def warn(msg):
  """
  Print nicely-formatted warning message.
  """
  sys.stderr.write('%s: warning: %s\n' % (me, msg))

def error(msg):
  """
  Print nicely-formatted error message and exit.
  """
  sys.stderr.write('%s: error: %s\n' % (me, msg))
  sys.exit(1)

def warn_if(cond, msg):
  if cond:
    warn(msg)

def error_if(cond, msg):
  if cond:
    error(msg)

def run(cmd, **kwargs):
  """
  Simple wrapper for subprocess.
  """
  if 'fatal' in kwargs:
    fatal = kwargs['fatal']
    del kwargs['fatal']
  else:
    fatal = False
  if 'tee' in kwargs:
    tee = kwargs['tee']
    del kwargs['tee']
  else:
    tee = False
  if isinstance(cmd, str):
    cmd = cmd.split(' ')
#  print(cmd)
  p = subprocess.run(cmd, stdin=None, capture_output=True, **kwargs)
  out = p.stdout.decode()
  err = p.stderr.decode()
  if fatal and p.returncode != 0:
    error("'%s' failed:\n%s%s" % (' '.join(cmd), out, err))
  if tee:
    sys.stdout.write(out)
    sys.stderr.write(err)
  return p.returncode, out, err

benches = {
    "SpacetimeDB": (
        "https://github.com/clockworklabs/SpacetimeDB",
        "69ec80331fe930c8c9160ab256b1858270d791ea",
        [("crates/bench", "cargo bench --bench generic --bench special")]
    ),
    "bevy": (
        "https://github.com/bevyengine/bevy",
        "de79d3f363e292489f2dbfdd22b6a9b93e7672ea",
        [("benches", "cargo bench")]
    ),
    "meilisearch": (
        "https://github.com/meilisearch/meilisearch",
        "8a0bf24ed5c0b49cb788a57ac19eaa43076962bf",
        [("", "cargo bench")]
    ),
    "oxipng": (
        "https://github.com/shssoichiro/oxipng",
        "788997c437319995e55030a92ed8294dfcd4c87a",
        [("", "cargo bench")]
    ),
    "tokio": (
        "https://github.com/tokio-rs/tokio",
        "9563707aaa73a802fa4d3c51c12869a037641070",
        [("", "cargo bench")]
    ),
    "ruff": (
        "https://github.com/astral-sh/ruff",
        "b302d89da3325c705f87a8343a16aad1723b67ab",
        [("crates/ruff_benchmark", "cargo bench")]
    ),
    "rav1e": (
        "https://github.com/xiph/rav1e",
        "6ee1f3a678deb9ccef2e3345168e39cd53e5d1a6",
        [("", "cargo criterion --features=bench")]
    ),
    "uv": (
        "https://github.com/astral-sh/uv",
        "dc5b3762f38a8e47b53bec9cc3cefb71e4aef55c",
        [("", "cargo bench --no-fail-fast")]
    ),
    "veloren": (
        "https://github.com/veloren/veloren",
        "8598d3d9c5c3a9e6d2366cfe882b479ce92a7bcc",
        [("", "cargo bench")]
    ),
    "zed": (
        "https://github.com/zed-industries/zed",
        "83d513aef48f6b4b56bad96740a02f5ef86a0a8c",
        [("crates/rope", "cargo bench"),
         ("crates/extension_host", "cargo bench")]
    ),
}

def main():
    class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
    parser = argparse.ArgumentParser(description="Simple benchmark runner",
                                     formatter_class=Formatter)
    parser.add_argument(
        "-t", "--toolchain", help="toolchain version to use", default=None
    )
    parser.add_argument(
        "-p", "--path", help="path to benchmark repos", default="./"
    )
    parser.add_argument(
        "-b",
        "--build-only",
        action="store_true",
        help="build but do not run benchmarks",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="clean repositores before running",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        help="limit build parallelism",
    )
    parser.add_argument(
        "-r",
        "--run-options",
        help="run under wrapper",
        default="taskset 0x1 nice -n -20 setarch -R",
    )
    parser.add_argument(
        "-o",
        "--only",
        help="comma-separated list of benchmarks to run",
    )
    parser.add_argument(
        "--clone",
        action="store_true",
        help="clone repos",
        default=False,
    )
    args = parser.parse_args()

    base_path = Path(os.path.abspath(args.path))
    os.makedirs(str(base_path), exist_ok=True)
    patch_root = Path(os.path.dirname(__file__))

    os.environ["CARGO_INCREMENTAL"] = "0"
    # See https://rust-lang.github.io/rustup/overrides.html
    os.environ["RUSTUP_TOOLCHAIN"] = args.toolchain

    # Rust is always line-buffered so mimic this here to preserve order
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    bench_names = sorted(benches.keys())
    if args.only is not None:
        bench_names = args.only.split(',')
        unknown_names = [name for name in bench_names if name not in benches.keys()]
        if unknown_names:
            error(f"unknown benchmarks {', '.join(unknown_names)}")

    # Clone

    if args.clone:
        for bench_name in bench_names:
            bench_repo, bench_branch, _ = benches[bench_name]
            print(f"Cloning {bench_repo}...")
            bench_path = base_path / os.path.basename(bench_repo)
            if not bench_path.exists():
                run(f"git clone {bench_repo}", cwd=str(base_path), fatal=True)
                run(f"git checkout {bench_branch}", cwd=str(bench_path), fatal=True)
                for bench_patch in sorted(glob.glob(str(patch_root / bench_name / "*.patch"))):
                    run(f"patch -p1 -i {bench_patch}", fatal=True, cwd=str(bench_path))

    # Build

    for bench_name in bench_names:
        bench_repo, _, bench_cmds = benches[bench_name]
        for bench_subdir, bench_params in bench_cmds:
            bench_build_path = base_path / os.path.basename(bench_repo) / bench_subdir
            print(f"Building {bench_build_path}...")

            error_if(not bench_build_path.exists(),
                     f"directory {bench_build_path} does not exist, did you forget to clone?")

            cargo_args = bench_params.split()

            if args.jobs is not None:
                cargo_args.extend(["-j", str(args.jobs)])

            cargo_args.append("--no-run")

            if args.clean:
                run(f"cargo clean", fatal=True, cwd=str(bench_build_path))

            run(cargo_args, fatal=True, cwd=str(bench_build_path))

    if args.build_only:
        return

    # Run

    for bench_name in bench_names:
        bench_repo, _, bench_cmds = benches[bench_name]
        print(f"Benching {bench_name}...")
        for bench_subdir, bench_params in bench_cmds:
            bench_path = base_path / os.path.basename(bench_repo) / bench_subdir

            cargo_args = args.run_options.split()
            cargo_args.extend(bench_params.split())

            run(cargo_args, fatal=True, tee=True, cwd=str(bench_path))

            # TODO: convert output to json

if __name__ == "__main__":
    main()
