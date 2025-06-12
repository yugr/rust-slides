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
import json
import re

me = os.path.basename(__file__)


def warn(msg):
    sys.stderr.write("%s: warning: %s\n" % (me, msg))


def error(msg):
    sys.stderr.write("%s: error: %s\n" % (me, msg))
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
    output_parser: Callable[str, dict]


def fix_units(units):
    return "us" if units == "µs" else units


def criterion_parser(bench_output: str) -> str:
    bench_runtimes = {}
    lines = bench_output.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()

        if not re.search(r"\btime: ", line):
            continue

        if line.startswith("time: "):
            # lexer/unicode/pypinyin.py
            #              time:   [23.196 µs 23.316 µs 23.452 µs]
            if i == 0 or lines[i - 1].strip() == "change:":
                continue
            name = lines[i - 1]
            full_line = lines[i - 1] + " " + line
        else:
            # lexer/pydantic/types.py time:   [204.06 µs 204.31 µs 204.62 µs]
            full_line = line

        match = re.match(r"(.+?)\s+time:\s*(\[.*)", full_line)
        error_if(match is None, f"failed to parse time report:\n{line}")
        name = match[1]
        data = match[2]

        data_match = re.match(
            r"^\[([0-9.]+) ([a-zµ]+) ([0-9.]+) ([a-zµ]+) ([0-9.]+) ([a-zµ]+)\]", data
        )
        error_if(data_match is None, f"failed to parse time report:\n{line}")
        bench_runtimes[name] = {
            "lb": (float(data_match[1]), fix_units(data_match[2])),
            "avg": (float(data_match[3]), fix_units(data_match[4])),
            "ub": (float(data_match[5]), fix_units(data_match[6])),
        }

    return bench_runtimes


def oxipng_parser(bench_output: str) -> str:
    bench_runtimes = {}
    lines = bench_output.splitlines()
    for line in lines:
        match = re.match(
            r"^test\s+(\S+)\s+\.\.\.\s+bench:\s+([0-9,.]+) ([a-z]+)/iter \(\+/- ([0-9,.]+)",
            line,
        )

        if match is None:
            continue

        name = match[1]
        time = float(match[2].replace(",", ""))
        units = match[3]
        diff = float(match[4].replace(",", ""))

        bench_runtimes[name] = {
            "lb": (time - diff, units),
            "avg": (time, units),
            "ub": (time + diff, units),
        }

    return bench_runtimes


benches = {
    "SpacetimeDB": Bench(
        "https://github.com/clockworklabs/SpacetimeDB",
        "69ec80331fe930c8c9160ab256b1858270d791ea",
        [("crates/bench", "cargo bench --bench generic --bench special")],
        criterion_parser,
    ),
    "bevy": Bench(
        "https://github.com/bevyengine/bevy",
        "de79d3f363e292489f2dbfdd22b6a9b93e7672ea",
        [("benches", "cargo bench")],
        criterion_parser,
    ),
    "meilisearch": Bench(
        "https://github.com/meilisearch/meilisearch",
        "8a0bf24ed5c0b49cb788a57ac19eaa43076962bf",
        [("", "cargo bench")],
        criterion_parser,
    ),
    "oxipng": Bench(
        "https://github.com/shssoichiro/oxipng",
        "788997c437319995e55030a92ed8294dfcd4c87a",
        [("", "cargo bench")],
        oxipng_parser,
    ),
    "tokio": Bench(
        "https://github.com/tokio-rs/tokio",
        "9563707aaa73a802fa4d3c51c12869a037641070",
        [("", "cargo bench")],
        criterion_parser,
    ),
    "ruff": Bench(
        "https://github.com/astral-sh/ruff",
        "b302d89da3325c705f87a8343a16aad1723b67ab",
        [("crates/ruff_benchmark", "cargo bench")],
        criterion_parser,
    ),
    "rav1e": Bench(
        "https://github.com/xiph/rav1e",
        "6ee1f3a678deb9ccef2e3345168e39cd53e5d1a6",
        [("", "cargo criterion --features=bench")],
        criterion_parser,
    ),
    "uv": Bench(
        "https://github.com/astral-sh/uv",
        "dc5b3762f38a8e47b53bec9cc3cefb71e4aef55c",
        [("", "cargo bench --no-fail-fast")],
        criterion_parser,
    ),
    "veloren": Bench(
        "https://github.com/veloren/veloren",
        "8598d3d9c5c3a9e6d2366cfe882b479ce92a7bcc",
        [("", "cargo bench")],
        criterion_parser,
    ),
    "zed": Bench(
        "https://github.com/zed-industries/zed",
        "83d513aef48f6b4b56bad96740a02f5ef86a0a8c",
        [("crates/rope", "cargo bench"), ("crates/extension_host", "cargo bench")],
        criterion_parser,
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
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Simple benchmark runner", formatter_class=Formatter
    )
    parser.add_argument(
        "-t", "--toolchain", help="toolchain version to use", default=None
    )
    parser.add_argument("-p", "--path", help="path to benchmark repos", default="./")
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
        "-q",
        "--quiet",
        help="do not print bench output",
        default=False,
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

    base_path = Path(args.path).absolute()
    os.makedirs(str(base_path), exist_ok=True)

    patch_root = Path(__file__).parent.absolute()

    os.environ["CARGO_INCREMENTAL"] = "0"
    # See https://rust-lang.github.io/rustup/overrides.html
    if args.toolchain:
        os.environ["RUSTUP_TOOLCHAIN"] = args.toolchain

    # Rust is always line-buffered so mimic this here to preserve order
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    bench_names = sorted(benches.keys())

    for bench_name in bench_names:
        for json_path in glob.glob(str(base_path / f"{bench_name}_*.json")):
            if os.path.isfile(json_path):
                os.unlink(json_path)

    if args.only is not None:
        bench_names = args.only.split(",")
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
                    run(f"patch -p1 -i {bench_patch}", fatal=True, cwd=str(bench_path))

    # Build

    for bench_name in bench_names:
        bench = benches[bench_name]
        for bench_subdir, bench_params in bench.launch_info:
            bench_build_path = (
                base_path / os.path.basename(bench.repo_link) / bench_subdir
            )
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
        for i, (bench_subdir, bench_params) in enumerate(bench.launch_info):
            bench_path = base_path / os.path.basename(bench.repo_link) / bench_subdir

            cargo_args = args.run_options.split()
            cargo_args.extend(bench_params.split())

            _, out, _ = run(
                cargo_args, fatal=True, tee=not args.quiet, cwd=str(bench_path)
            )
            json = bench.output_parser(out)
            with (base_path / f"{bench_name}_{i}.json").open("w") as f:
                f.write(json.dumps(bench_runtimes, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
