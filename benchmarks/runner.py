#!/usr/bin/env python3

from __future__ import annotations

import argparse
import glob
import os
import os.path
from pathlib import Path
import subprocess
import sys
from dataclasses import dataclass
from collections.abc import Callable

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


@dataclass
class Bench:
    repo_link: str
    commit: str
    launch_info: list[tuple[str, str]]
    output_parser: Callable[str, str]

def parser_stub(bench_output: str) -> str:
    return bench_output

benches = {
    "SpacetimeDB": Bench(
        "https://github.com/clockworklabs/SpacetimeDB",
        "69ec80331fe930c8c9160ab256b1858270d791ea",
        [("crates/bench", "cargo bench --bench generic --bench special")],
        parser_stub,
    ),
    "bevy": Bench(
        "https://github.com/bevyengine/bevy",
        "de79d3f363e292489f2dbfdd22b6a9b93e7672ea",
        [("benches", "cargo bench")],
        parser_stub,
    ),
    "meilisearch": Bench(
        "https://github.com/meilisearch/meilisearch",
        "8a0bf24ed5c0b49cb788a57ac19eaa43076962bf",
        [("", "cargo bench")],
        parser_stub,
    ),
    "oxipng": Bench(
        "https://github.com/shssoichiro/oxipng",
        "788997c437319995e55030a92ed8294dfcd4c87a",
        [("", "cargo bench")],
        parser_stub,
    ),
    "tokio": Bench(
        "https://github.com/tokio-rs/tokio",
        "9563707aaa73a802fa4d3c51c12869a037641070",
        [("", "cargo bench")],
        parser_stub,
    ),
    "ruff": Bench(
        "https://github.com/astral-sh/ruff",
        "b302d89da3325c705f87a8343a16aad1723b67ab",
        [("crates/ruff_benchmark", "cargo bench")],
        parser_stub,
    ),
    "rav1e": Bench(
        "https://github.com/xiph/rav1e",
        "6ee1f3a678deb9ccef2e3345168e39cd53e5d1a6",
        [("", "cargo criterion --features=bench")],
        parser_stub,
    ),
    "uv": Bench(
        "https://github.com/astral-sh/uv",
        "dc5b3762f38a8e47b53bec9cc3cefb71e4aef55c",
        [("", "cargo bench --no-fail-fast")],
        parser_stub,
    ),
    "veloren": Bench(
        "https://github.com/veloren/veloren",
        "8598d3d9c5c3a9e6d2366cfe882b479ce92a7bcc",
        [("", "cargo bench")],
        parser_stub,
    ),
    "zed": Bench(
        "https://github.com/zed-industries/zed",
        "83d513aef48f6b4b56bad96740a02f5ef86a0a8c",
        [("crates/rope", "cargo bench"), ("crates/extension_host", "cargo bench")],
        parser_stub,
    ),
}


def run(cmd, fatal=False, tee=False, **kwargs):
    """
    Simple wrapper for subprocess.
    """
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    #  print(cmd)
    p = subprocess.run(cmd, stdin=None, capture_output=True, **kwargs)
    out = p.stdout.decode()
    err = p.stderr.decode()
    if fatal and p.returncode != 0:
        error("'%s' failed:\n%s%s" % (" ".join(cmd), out, err))
    if tee:
        sys.stdout.write(out)
        sys.stderr.write(err)
    return p.returncode, out, err


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
    if args.toolchain:
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
            bench = benches[bench_name]
            print(f"Cloning {bench.repo_link}...")
            bench_path = base_path / os.path.basename(bench.repo_link)
            if not bench_path.exists():
                run(f"git clone {bench.repo_link}", cwd=str(base_path), fatal=True)
                run(f"git checkout {bench.commit}", cwd=str(bench_path), fatal=True)
                for bench_patch in sorted(
                    glob.glob(str(patch_root / bench_name / "*.patch"))
                ):
                    run(f"patch -p1 -i {Path(bench_patch).absolute()}", fatal=True, cwd=str(bench_path))

    # Build

    for bench_name in bench_names:
        bench = benches[bench_name]
        for bench_subdir, bench_params in bench.launch_info:
            bench_build_path = base_path / os.path.basename(bench.repo_link) / bench_subdir
            print(f"Building {bench_build_path}...")

            error_if(
                not bench_build_path.exists(),
                f"directory {bench_build_path} does not exist, did you forget to clone?",
            )

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
        bench = benches[bench_name]
        print(f"Benching {bench_name}...")
        for bench_subdir, bench_params in bench.launch_info:
            bench_path = base_path / os.path.basename(bench.repo_link) / bench_subdir

            cargo_args = args.run_options.split()
            cargo_args.extend(bench_params.split())

            run(cargo_args, fatal=True, tee=True, cwd=str(bench_path))

            # TODO: convert output to json

if __name__ == "__main__":
    main()
