#!/usr/bin/env python3

# Runner for Rust benchmarks.
#
# TODO:
#   - type annotations

import argparse
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
VERBOSE = 0


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


class ExecutionError(Exception):
    pass


class BuildError(Exception):
    pass


def run(cmd, fatal=True, tee=False, **kwargs):
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
        raise ExecutionError(f"'{cmds}' failed:\n{out}{err}")
    if tee:
        sys.stdout.write(out)
        sys.stderr.write(err)
    return p.returncode, out, err, (t2 - t1) / 1e9


def make_toc(words, renames=None):
    "Make an mapping of words to their indices in list"
    renames = renames or {}
    toc = {}
    for i, n in enumerate(words):
        name = renames.get(n, n)
        toc[i] = name
    return toc


def parse_row(words, toc, hex_keys):
    "Make a mapping from column names to values"
    vals = {k: (words[i] if i < len(words) else "") for i, k in toc.items()}
    for k in hex_keys:
        if vals[k]:
            vals[k] = int(vals[k], 16)
    return vals


def collect_sections(f):
    """Collect section info from ELF."""

    _, out, _, _ = run(["readelf", "-SW", f])

    toc = None
    sections = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"\[\s+", "[", line)
        words = re.split(r" +", line)
        if line.startswith("[Nr]"):  # Header?
            if toc is not None:
                error("multiple headers in output of readelf")
            toc = make_toc(words, {"Addr": "Address"})
        elif line.startswith("[") and toc is not None:
            sec = parse_row(words, toc, ["Address", "Off", "Size"])
            if "A" in sec["Flg"]:  # Allocatable section?
                sections.append(sec)

    if toc is None:
        error(f"failed to analyze sections in {f}")

    return sections


def maybe_collect_binary_sizes(f):
    """Collect sizes of important file segments."""

    if not f.is_file():
        return None

    rc, out, _, _ = run(f"file {f}", fatal=False)
    if rc != 0:
        return None

    if "ELF" not in out or "executable" not in out:
        return None

    sizes = {}
    for s in collect_sections(str(f)):
        name = s["Name"]
        # See -hotcoldsplit-cold-section-name default
        if name.startswith(".text") or name == "__llvm_cold":
            target = "text"
        elif name.startswith(".rodata"):
            target = "rodata"
        elif name.startswith(".eh_frame") or name == ".gcc_except_table":
            target = "eh"
        else:
            continue
        sizes[target] = sizes.get(target, 0) + s["Size"]

    return sizes


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

        run(f"git clone {self.repo}", cwd=str(base_path))
        run(f"git checkout {self.commit}", cwd=str(bench_path))

        patch_root = Path(__file__).parent.absolute()
        for bench_patch in sorted((patch_root / self.name).glob("*.patch")):
            run(f"patch -p1 -i {bench_patch}", cwd=str(bench_path))

    def build(self, repo_path, clean, jobs, timeout):
        raise NotImplementedError

    def run(self, repo_path, run_options):
        raise NotImplementedError


class CargoBench(Bench):
    """Base class for benchmarks which use 'cargo bench' interface."""

    def __init__(self, name, repo, commit, build_cmds, bench_cmds):
        super().__init__(name, repo, commit)
        self.build_cmds = build_cmds
        self.bench_cmds = bench_cmds

    def build(self, repo_path, clean, jobs, timeout):
        cargo_parallel = [] if jobs is None else [f"-j{jobs}"]

        if clean:
            run("cargo clean", cwd=str(repo_path))

        # Run main build cmd

        for build_cmd in self.build_cmds:
            cargo_args = build_cmd.split()
            if not any(arg.startswith("-j") for arg in cargo_args):
                cargo_args.extend(cargo_parallel)
            try:
                run(cargo_args, tee=(VERBOSE > 0), cwd=str(repo_path), timeout=timeout)
            except ExecutionError as e:
                raise BuildError(*e.args) from None

        # Build each bench
        # TODO: do we need this ?

        for subdir, params in self.bench_cmds:
            build_path = repo_path / subdir

            if not build_path.exists():
                raise BuildError(
                    f"directory {build_path} does not exist, did you forget to clone?"
                )

            cargo_args = params.split()
            cargo_args.extend(cargo_parallel)
            cargo_args.append("--no-run")
            try:
                run(cargo_args, tee=(VERBOSE > 0), cwd=str(build_path), timeout=timeout)
            except ExecutionError as e:
                raise BuildError(*e.args) from None

        # Collect ELF sizes

        binary_path = Path(repo_path) / "target" / "release"

        sizes = {}
        for f in binary_path.iterdir():
            sz = maybe_collect_binary_sizes(f)
            if sz is not None:
                sizes[f.name] = sz

        return sizes

    def run(self, repo_path, run_options):
        runtimes = []

        for subdir, params in self.bench_cmds:
            build_path = repo_path / subdir

            cargo_args = run_options.split()
            cargo_args.extend(params.split())

            global QUIET
            _, out, _, _ = run(cargo_args, tee=not QUIET, cwd=str(build_path))

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
            if match is None:
                raise ExecutionError(f"failed to parse time report:\n{line}")
            name = match[1]
            data = match[2]

            data_match = re.match(
                r"^\[([0-9.]+) ([a-zµ]+) ([0-9.]+) ([a-zµ]+) ([0-9.]+) ([a-zµ]+)\]",
                data,
            )
            if data_match is None:
                raise ExecutionError(f"failed to parse time report:\n{line}")
            runtimes[name] = {
                "lb": (float(data_match[1]), fix_units(data_match[2])),
                "avg": (float(data_match[3]), fix_units(data_match[4])),
                "ub": (float(data_match[5]), fix_units(data_match[6])),
            }

        return runtimes


class UVBench(CriterionBench):
    """UV benchmark class."""

    def build(self, repo_path, clean, jobs, timeout):
        venv_path = repo_path / ".venv"
        if not venv_path.exists():
            run("python3 -m venv .venv", cwd=repo_path, timeout=timeout)
        return super().build(repo_path, clean, jobs)


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

        if not runtimes:
            raise ExecutionError(f"failed to parse oxipng time report:\n{out}")

        return runtimes


class RegexBench(Bench):
    """Class for BurntSushi regex benchmarks."""

    def build(self, repo_path, clean, jobs, timeout):
        if clean:
            run("cargo clean", cwd=str(repo_path))
            engine_path = repo_path / "engines/rust/regex"
            run("cargo clean", cwd=str(engine_path))

        cargo_args = ["cargo", "build", "--release"]
        if jobs is not None:
            cargo_args.append(f"-j{jobs}")
        run(cargo_args, tee=(VERBOSE > 0), cwd=str(repo_path), timeout=timeout)

        run("target/release/rebar build -e ^rust/regex$", tee=(VERBOSE > 0), cwd=str(repo_path), timeout=timeout)

        # TODO: collect sizes
        return {}

    def run(self, repo_path, run_options):
        # TODO: rebar also supports other Rust regex engines (regex-lite, regress)
        _, out, _, _ = run(
            run_options + " target/release/rebar measure -e ^rust/regex$ -f ^curated",
            tee=(VERBOSE > 0),
            # "target/release/rebar measure -e ^rust/regex$ -f ^unicode/compile/fifty-letters$"
            cwd=str(repo_path),
        )

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


class RustcBench(Bench):
    def build(self, repo_path, clean, jobs, timeout):
        # Build

        bench_path = Path(repo_path) / "collector" / "runtime-benchmarks"
        for subdir in bench_path.iterdir():
            if not subdir.is_dir() or subdir.name == "data":
                continue
            if clean:
                run("cargo clean", cwd=str(subdir))
            build_args = ["cargo", "build", "--release"]
            if jobs is not None:
                build_args.append(f"-j{jobs}")
            try:
                run(build_args, tee=(VERBOSE > 0), cwd=str(subdir), timeout=timeout)
            except ExecutionError as e:
                raise BuildError(*e.args) from None

        # Collect sizes

        sizes = {}
        for d in bench_path.iterdir():
            binary_path = d / "target" / "release"
            if not d.is_dir() or not binary_path.exists():
                continue
            for f in binary_path.iterdir():
                sz = maybe_collect_binary_sizes(f)
                if sz is not None:
                    sizes[f.name] = sz

        return sizes

    def run(self, repo_path, run_options):
        runtimes = {}
        bench_path = Path(repo_path) / "collector" / "runtime-benchmarks"
        for subdir in bench_path.iterdir():
            if not subdir.is_dir() or subdir.name == "data":
                continue
            run_args = run_options if run_options else ""
            run_args += f" ./target/release/{subdir.name}-bench run"
            _, out, _, _ = run(run_args, cwd=str(subdir))

            for bench_line in out.splitlines():
                benchmark_data = json.loads(bench_line)["Result"]
                times = []
                for run_result in benchmark_data["stats"]:
                    times.append(
                        int(run_result["wall_time"]["secs"]) * int(1e9)
                        + int(run_result["wall_time"]["nanos"])
                    )

                runtimes[benchmark_data["name"]] = {
                    "lb": (min(times), "ns"),
                    "avg": (sum(times) / len(times), "ns"),
                    "ub": (max(times), "ns"),
                }
        return [runtimes]


BENCHES = [
    CriterionBench(
        "SpacetimeDB",
        "https://github.com/clockworklabs/SpacetimeDB",
        "69ec80331fe930c8c9160ab256b1858270d791ea",
        ["cargo b --profile bench --lib --bins --benches"],
        [("crates/bench", "cargo bench --bench generic --bench special")],
    ),
    CriterionBench(
        "bevy",
        "https://github.com/bevyengine/bevy",
        "de79d3f363e292489f2dbfdd22b6a9b93e7672ea",
        ["cargo b --profile bench --lib --bins --benches"],
        [("benches", "cargo bench")],
    ),
    CriterionBench(
        "meilisearch",
        "https://github.com/meilisearch/meilisearch",
        "0fd66a5317da7e1f075058665944cac62e17d446",
        ["cargo b --profile bench --lib --bins --benches"],
        [("", "cargo bench")],
    ),
    CriterionBench(
        "nalgebra",
        "https://github.com/dimforge/nalgebra",
        "v0.33.2",
        ["cargo b --profile bench --lib --bins --benches"],
        [("", "cargo bench")],
    ),
    OxipngBench(
        "oxipng",
        "https://github.com/shssoichiro/oxipng",
        "788997c437319995e55030a92ed8294dfcd4c87a",
        ["cargo b --profile bench --lib --bins --benches"],
        [("", "cargo bench")],
    ),
    CriterionBench(
        "rav1e",
        "https://github.com/xiph/rav1e",
        "6ee1f3a678deb9ccef2e3345168e39cd53e5d1a6",
        ["cargo b --profile bench --lib --bins --benches"],
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
        ["cargo b --profile bench --lib --bins --benches"],
        [("crates/ruff_benchmark", "cargo bench")],
    ),
    RustcBench(
        "rustc-runtime-benchmarks",
        "https://github.com/rust-lang/rustc-perf",
        "2f1d1c27e7a2342d4cbdfea5fb7eac226e70111c",
    ),
    CriterionBench(
        "rust_serialization_benchmark",
        "https://github.com/djkoloski/rust_serialization_benchmark",
        "cd9d93b0b0d2036dfb2ec4037cc6f37cf6cab291",
        ["cargo b --profile bench --lib --bins --benches"],
        [("", "cargo bench")],
    ),
    CriterionBench(
        "tokio",
        "https://github.com/tokio-rs/tokio",
        "9563707aaa73a802fa4d3c51c12869a037641070",
        ["cargo b --profile bench --lib --bins --benches"],
        [("", "cargo bench")],
    ),
    UVBench(
        "uv",
        "https://github.com/astral-sh/uv",
        "dc5b3762f38a8e47b53bec9cc3cefb71e4aef55c",
        ["cargo b --profile bench --lib --bins --benches"],
        [("", "cargo bench")],
    ),
    CriterionBench(
        "veloren",
        "https://github.com/veloren/veloren",
        "8598d3d9c5c3a9e6d2366cfe882b479ce92a7bcc",
        [
            "cargo b --profile bench --lib --benches",
            "cargo b --profile bench --bins -j1",  # Work around OOMs
        ],
        [("", "cargo bench")],
    ),
    CriterionBench(
        "zed",
        "https://github.com/zed-industries/zed",
        "83d513aef48f6b4b56bad96740a02f5ef86a0a8c",
        ["cargo b --profile bench --bins --benches"],  # Fails with --lib
        [("crates/rope", "cargo bench")],
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
        "--build-timeout",
        help="timeout for building and running each benchmark",
    )
    parser.add_argument(
        "-c",
        "--clean",
        dest="clean",
        action="store_true",
        help="clean repositores before running",
        default=True,
    )
    parser.add_argument(
        "--no-clean",
        dest="clean",
        action="store_false",
        help="Inverse of --clean",
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
        default="setarch -R",
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
    parser.add_argument(
        "-v",
        "--verbose",
        help="print build logs",
        action="count",
        default=0,
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

    global VERBOSE
    VERBOSE = args.verbose

    global BENCHES
    benches = BENCHES

    for bench in benches:
        for json_path in base_path.glob(f"{bench.name}_*.json"):
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

    failed_benches = set()
    for bench in benches:
        print(f"Building {bench.name}...")
        repo_path = base_path / os.path.basename(bench.repo)
        try:
            t1 = time.time()
            build_times = bench.build(repo_path, args.clean, args.jobs, args.build_timeout)
            elapsed = time.time() - t1
            with (base_path / f"{bench.name}_sizes.json").open("w") as f:
                f.write(json.dumps(build_times, indent=4, sort_keys=True))
            print(f"Built successfully in {int(elapsed)} sec.")
        except BuildError as e:
            failed_benches.add(bench)
            warn(f"{bench.name}: failed to build:\n{e.args[0]}")

    if args.build_only:
        if failed_benches:
            print(f"Failed to build {len(failed_benches)} benchmarks")
            return 1
        return 0

    # Run

    for bench in (b for b in benches if b not in failed_benches):
        print(f"Benching {bench.name}...")
        repo_path = base_path / os.path.basename(bench.repo)
        try:
            t1 = time.time()
            for i, bench_runtimes in enumerate(bench.run(repo_path, args.run_options)):
                with (base_path / f"{bench.name}_{i}.json").open("w") as f:
                    f.write(json.dumps(bench_runtimes, indent=4, sort_keys=True))
            elapsed = time.time() - t1
            print(f"Benched successfully in {int(elapsed)} sec.")
        except ExecutionError as e:
            failed_benches.add(bench)
            warn(f"{bench.name}: failed to run\n{e.args[0]}")

    if failed_benches:
        print(f"Failed to bench {len(failed_benches)} benchmarks")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
