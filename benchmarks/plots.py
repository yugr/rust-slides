#!/usr/bin/python3

# Plots benchmark results for Rust benchmarks.

import argparse
import atexit
import multiprocessing
import os
import os.path
import re
import shutil
import subprocess
import statistics
import sys
import tempfile
from typing import NoReturn

me = os.path.basename(__file__)
average_mode = "median"


def warn(msg):
    """
    Print nicely-formatted warning message.
    """
    sys.stderr.write(f"{me}: warning: {msg}\n")


def error(msg) -> NoReturn:
    """
    Print nicely-formatted error message and exit.
    """
    sys.stderr.write(f"{me}: error: {msg}\n")
    sys.exit(1)


def warn_if(cond, msg):
    if cond:
        warn(msg)


def error_if(cond, msg):
    if cond:
        error(msg)


def run(cmd, fatal=True, tee=False, **kwargs):
    """
    Simple wrapper for subprocess.
    """
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    # print(cmd)
    p = subprocess.run(
        cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs
    )
    out = p.stdout.decode()
    err = p.stderr.decode()
    if fatal and p.returncode != 0:
        cmds = " ".join(cmd)
        error(f"'{cmds}' failed:\n{out}{err}")
    if tee:
        sys.stdout.write(out)
        sys.stderr.write(err)
    return p.returncode, out, err


def collect_results(builds, baseline, tmp_dir):
    all_builds = set(builds)
    all_builds.add(baseline)

    compare = os.path.join(os.path.dirname(__file__), "compare.py")

    results = {}

    for b in builds:
        _, out, _ = run([compare, baseline, b])

        build_name = os.path.basename(b.rstrip('/'))

        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue

            # SpacetimeDB_0.json: +0.8%
            # SpacetimeDB_sizes.json rodata: -0.0%
            # SpacetimeDB_sizes.json text: +3.9%
            m = re.match(r'^(.*)(?:_sizes)?\.json(.*): (.*)%$', line)
            error_if(m is None, f"failed to parse compare.py output: {line}")

            name = m[1]
            typ = m[2].strip() or 'perf'
            diff = float(m[3])

            results.setdefault(typ, {}).setdefault(build_name, {})[name] = diff

    return results


def generate_plots(results, out_dir):
    print(results)  # TODO


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Generate Rust benchmarks plots",
        formatter_class=Formatter,
        epilog=f"""\
Examples:
  $ {me} path/to/build1 path/to/build2 ...
""",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Print diagnostic info (can be specified more than once)",
        action="count",
        default=0,
    )
    parser.add_argument(
        "-o",
        help="Path to store results",
        default=".",
    )
    parser.add_argument(
        "--baseline",
        help="Path to baseline build to compare against",
    )
    parser.add_argument(
        "--tmp-dir",
        help="Path to store temporary files",
    )
    parser.add_argument(
        "builds",
        nargs=argparse.REMAINDER,
        default=[],
        help="List of paths to build results to plot",
    )

    args = parser.parse_args()

    if args.tmp_dir is not None:
        tmp_dir = args.tmp_dir
    else:
        tmp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(tmp_dir))

    baseline = args.baseline or os.path.join(os.path.dirname(args.builds[0]), '..', 'baseline')

    results = collect_results(args.builds, baseline, tmp_dir)

    generate_plots(results, args.o)

    return 0


if __name__ == "__main__":
    sys.exit(main())
