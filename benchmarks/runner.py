#!/usr/bin/env python3

# Runner for Rust benchmarks.
#
# TODO:
#   - type annotations

import argparse
import glob
import json
import os
import os.path
from pathlib import Path
import subprocess
import sys
import re
import time

me = os.path.basename(__file__)

QUIET = False


def warn(msg):
    sys.stderr.write(f"{me}: warning: {msg}\n")


def error(msg):
    sys.stderr.write(f"{me}: error: {msg}\n")
    sys.exit(1)


def warn_if(cond, msg):
    if cond:
        warn(msg)


def error_if(cond, msg):
    if cond:
        error(msg)


def run(cmd, fatal=False, tee=False, **kwargs):
    """
    Simple wrapper for subprocess.
    """
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    #  print(cmd)
    t1 = time.perf_counter_ns()
    p = subprocess.run(cmd, stdin=None, capture_output=True, **kwargs)
    t2 = time.perf_counter_ns()
    out = p.stdout.decode()
    err = p.stderr.decode()
    if fatal and p.returncode != 0:
        cmds = " ".join(cmd)
        error(f"'{cmds}' failed:\n{out}{err}")
    if tee:
        sys.stdout.write(out)
        sys.stderr.write(err)
    return p.returncode, out, err, (t2 - t1) / 1e9


class Bench:
    """Base class for all benchmarks."""

    def __init__(self, name, repo, commit):
        self.name = name
        self.repo = repo
        self.commit = commit

    def clone(self, base_path):
        bench_path = base_path / os.path.basename(self.repo)
        if bench_path.exists():
            return

        run(f"git clone {self.repo}", cwd=str(base_path), fatal=True)
        run(f"git checkout {self.commit}", cwd=str(bench_path), fatal=True)

        patch_root = Path(__file__).parent.absolute()
        for bench_patch in sorted(glob.glob(str(patch_root / self.name / "*.patch"))):
            run(f"patch -p1 -i {bench_patch}", fatal=True, cwd=str(bench_path))

    def build(self, base_path, clean, jobs):
        raise NotImplementedError

    def run(self, base_path, run_options):
        raise NotImplementedError


class CargoBench(Bench):
    """Base class for benchmarks which use 'cargo bench' interface."""

    def __init__(self, name, repo, commit, cmds):
        super().__init__(name, repo, commit)
        self.cmds = cmds

    def build(self, base_path, clean, jobs):
        for subdir, params in self.cmds:
            build_path = base_path / os.path.basename(self.repo) / subdir

            error_if(
                not build_path.exists(),
                f"directory {build_path} does not exist, did you forget to clone?",
            )

            if clean:
                run("cargo clean", fatal=True, cwd=str(build_path))

            cargo_args = params.split()
            if jobs is not None:
                cargo_args.extend(["-j", str(jobs)])
            cargo_args.append("--no-run")
            run(cargo_args, fatal=True, cwd=str(build_path))

    def run(self, base_path, run_options):
        runtimes = []

        for subdir, params in self.cmds:
            build_path = base_path / os.path.basename(self.repo) / subdir

            cargo_args = run_options.split()
            cargo_args.extend(params.split())

            global QUIET
            _, out, _, _ = run(
                cargo_args, fatal=True, tee=not QUIET, cwd=str(build_path)
            )

            runtimes.append(self.parse(out))

        return runtimes

    def parse(self, out):
        raise NotImplementedError


def fix_units(units):
    return "us" if units == "µs" else units


class CriterionBench(CargoBench):
    """Base class for benchmarks which use Criterion harness."""

    def parse(self, out):
        runtimes = {}

        lines = out.splitlines()
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
                r"^\[([0-9.]+) ([a-zµ]+) ([0-9.]+) ([a-zµ]+) ([0-9.]+) ([a-zµ]+)\]",
                data,
            )
            error_if(data_match is None, f"failed to parse time report:\n{line}")
            runtimes[name] = {
                "lb": (float(data_match[1]), fix_units(data_match[2])),
                "avg": (float(data_match[3]), fix_units(data_match[4])),
                "ub": (float(data_match[5]), fix_units(data_match[6])),
            }

        return runtimes


class OxipngBench(CargoBench):
    """Oxipng benchmark class."""

    def parse(self, out):
        runtimes = {}

        for line in out.splitlines():
            match = re.match(
                r"^test\s+(\S+)\s+\.\.\.\s+bench:\s+([0-9,.]+) ([a-z]+)/iter \(\+/- ([0-9,.]+)",
                line,
            )

            if match is None:
                continue

            name = match[1]
            t = float(match[2].replace(",", ""))
            units = match[3]
            diff = float(match[4].replace(",", ""))

            runtimes[name] = {
                "lb": (t - diff, units),
                "avg": (t, units),
                "ub": (t + diff, units),
            }

        return runtimes


class RegexBench(Bench):
    """Class for BurntSushi regex benchmarks."""

    def build(self, base_path, clean, jobs):
        build_path = base_path / os.path.basename(self.repo)

        if clean:
            run("cargo clean", fatal=True, cwd=str(build_path))

        cargo_args = ["cargo", "build", "--release"]
        if jobs is not None:
            cargo_args.extend(["-j", str(jobs)])
        run(cargo_args, fatal=True, cwd=str(build_path))

        run(
            "target/release/rebar build -e ^rust/regex$",
            fatal=True,
            cwd=str(build_path),
        )

    def run(self, base_path, run_options):
        build_path = base_path / os.path.basename(self.repo)

        # TODO: rebar also supports otherRust regex engines (regex-lite, regress)
        _, out, _, _ = run(
            "target/release/rebar measure -e ^rust/regex$ -f ^curated",
            fatal=True,
            cwd=str(build_path),
        )
        #        _, out, _, _ = run("target/release/rebar measure -e ^rust/regex$ -f ^unicode/compile/fifty-letters$", fatal=True, cwd=str(build_path))

        lines = out.splitlines()

        idx = {name: i for i, name in enumerate(lines[0].split(","))}

        runtimes = {}

        def parse_time(t):
            match = re.match(r"([0-9.]+)([a-zµ]+)", t)
            return float(match[1]), fix_units(match[2])

        for line in lines[1:]:
            vals = line.split(",")

            name = vals[idx["name"]]
            mean = vals[idx["mean"]]
            min = vals[idx["min"]]
            max = vals[idx["max"]]

            runtimes[name] = {
                "lb": parse_time(min),
                "avg": parse_time(mean),
                "ub": parse_time(max),
            }

        return [runtimes]


BENCHES = [
    CriterionBench(
        "SpacetimeDB",
        "https://github.com/clockworklabs/SpacetimeDB",
        "69ec80331fe930c8c9160ab256b1858270d791ea",
        [("crates/bench", "cargo bench --bench generic --bench special")],
    ),
    CriterionBench(
        "bevy",
        "https://github.com/bevyengine/bevy",
        "de79d3f363e292489f2dbfdd22b6a9b93e7672ea",
        [("benches", "cargo bench")],
    ),
    CriterionBench(
        "meilisearch",
        "https://github.com/meilisearch/meilisearch",
        "8a0bf24ed5c0b49cb788a57ac19eaa43076962bf",
        [("", "cargo bench")],
    ),
    CriterionBench(
        "nalgebra",
        "https://github.com/dimforge/nalgebra",
        "v0.33.2",
        [("", "cargo bench")],
    ),
    OxipngBench(
        "oxipng",
        "https://github.com/shssoichiro/oxipng",
        "788997c437319995e55030a92ed8294dfcd4c87a",
        [("", "cargo bench")],
    ),
    CriterionBench(
        "rav1e",
        "https://github.com/xiph/rav1e",
        "6ee1f3a678deb9ccef2e3345168e39cd53e5d1a6",
        # Project suggests using "cargo criterion"
        # but it dumps output to stderr rather than stdout
        [("", "cargo bench --features=bench")],
    ),
    RegexBench(
        "regex",
        "https://github.com/BurntSushi/rebar",
        "19aa8e8e3bd3a4bc0ef6e07774d900e5f4840fad",
    ),
    CriterionBench(
        "ruff",
        "https://github.com/astral-sh/ruff",
        "b302d89da3325c705f87a8343a16aad1723b67ab",
        [("crates/ruff_benchmark", "cargo bench")],
    ),
    CriterionBench(
        "rust_serialization_benchmark",
        "https://github.com/djkoloski/rust_serialization_benchmark",
        "cd9d93b0b0d2036dfb2ec4037cc6f37cf6cab291",
        [("", "cargo bench")],
    ),
    CriterionBench(
        "tokio",
        "https://github.com/tokio-rs/tokio",
        "9563707aaa73a802fa4d3c51c12869a037641070",
        [("", "cargo bench")],
    ),
    CriterionBench(
        "uv",
        "https://github.com/astral-sh/uv",
        "dc5b3762f38a8e47b53bec9cc3cefb71e4aef55c",
        [("", "cargo bench --no-fail-fast")],
    ),
    CriterionBench(
        "veloren",
        "https://github.com/veloren/veloren",
        "8598d3d9c5c3a9e6d2366cfe882b479ce92a7bcc",
        [("", "cargo bench")],
    ),
    CriterionBench(
        "zed",
        "https://github.com/zed-industries/zed",
        "83d513aef48f6b4b56bad96740a02f5ef86a0a8c",
        [("crates/rope", "cargo bench"), ("crates/extension_host", "cargo bench")],
    ),
]


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

    os.environ["CARGO_INCREMENTAL"] = "0"
    # See https://rust-lang.github.io/rustup/overrides.html
    if args.toolchain:
        os.environ["RUSTUP_TOOLCHAIN"] = args.toolchain

    # Rust is always line-buffered so mimic this here to preserve order
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    global QUIET
    QUIET = args.quiet

    global BENCHES
    benches = BENCHES

    for bench in benches:
        for json_path in glob.glob(str(base_path / f"{bench.name}_*.json")):
            os.unlink(json_path)

    if args.only is not None:
        only_names = args.only.split(",")
        known_names = [bench.name for bench in benches]
        unknown_names = [name for name in only_names if name not in known_names]
        error_if(unknown_names, f"unknown benchmarks {', '.join(unknown_names)}")
        benches = [bench for bench in benches if bench.name in only_names]

    # Clone

    if args.clone:
        for bench in benches:
            print(f"Cloning {bench.name}...")
            bench.clone(base_path)

    # Build

    for bench in benches:
        print(f"Building {bench.name}...")
        t1 = time.time()
        bench.build(base_path, args.clean, args.jobs)
        elapsed = time.time() - t1
        print(f"Built successfully in {int(elapsed)} sec.")

    if args.build_only:
        return

    # Run

    for bench in benches:
        print(f"Benching {bench.name}...")
        t1 = time.time()
        for i, bench_runtimes in enumerate(bench.run(base_path, args.run_options)):
            with (base_path / f"{bench.name}_{i}.json").open("w") as f:
                f.write(json.dumps(bench_runtimes, indent=4, sort_keys=True))
        elapsed = time.time() - t1
        print(f"Benched successfully in {int(elapsed)} sec.")


if __name__ == "__main__":
    main()
