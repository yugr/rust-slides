#!/usr/bin/python3

# Plots benchmark results for C++ benchmarks (Clang, ffmpeg, PTS).

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


import matplotlib.pyplot as plt
import pandas as pd

ME = os.path.basename(__file__)
DEFAULT_VALUE = -0.1


def warn(msg):
    """
    Print nicely-formatted warning message.
    """
    sys.stderr.write(f"{ME}: warning: {msg}\n")


def error(msg) -> NoReturn:
    """
    Print nicely-formatted error message and exit.
    """
    sys.stderr.write(f"{ME}: error: {msg}\n")
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
    else:
        cmd = [str(arg) for arg in cmd]
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


def get_baseline(b):
    return "Libcxx" if b in ("Libcxx", "HardenedSTL") else "Baseline"


def collect_pts_results(builds, pts_dir, tmp_dir, average_mode):
    all_builds = set(builds)
    all_builds.add("Baseline")
    if "HardenedSTL" in builds:
        all_builds.add("Libcxx")

    parser = os.path.join(os.path.dirname(__file__), "PTS", "parser.py")
    compare = os.path.join(os.path.dirname(__file__), "..", "compare.py")

    for b in all_builds:
        f = os.path.join(pts_dir, b + ".log")
        error_if(not os.path.exists(f), f"PTS result file {f} does not exist")

        o = os.path.join(tmp_dir, b)
        run(
            [parser, "--std-threshold", 0.5, "--average-mode", average_mode, "-o", o, f]
        )

    results = {}

    for b in builds:
        base = os.path.join(tmp_dir, get_baseline(b))
        o = os.path.join(tmp_dir, b)
        _, out, _ = run([compare, "--ignore-missing", base, o])

        results[b] = {}
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(.*): (.*)%$", line)
            error_if(m is None, f"failed to parse compare.py output: {line}")
            name = re.sub(r"-[0-9.]+(-git)?\.json", "", m[1])
            val = float(m[2])
            # Filter out noise
            val = DEFAULT_VALUE if (val > 0 or abs(val) < 1) else val
            results[b][name] = val

    return results


def average_times(filename, average_mode):
    with open(filename) as f:
        lines = f.readlines()

    times = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([0-9.]+)user ", line)
        if m is None:
            continue
        times.append(float(m[1]))

    if average_mode == "median":
        return statistics.median(times)
    elif average_mode == "mean":
        return statistics.mean(times)
    elif average_mode == "min":
        return min(times)

    assert False


def collect_ffmpeg_results(builds, ffmpeg_dir, tmp_dir, average_mode):
    results = {}

    for b in builds:
        t0 = average_times(
            os.path.join(ffmpeg_dir, get_baseline(b) + ".log"), average_mode
        )
        t = average_times(os.path.join(ffmpeg_dir, b + ".log"), average_mode)
        results[b] = {"ffmpeg": 100 * (t0 - t) / t0}

    return results


def collect_llvm_results(builds, llvm_dir, tmp_dir, average_mode):
    results = {}

    for b in builds:
        t0 = average_times(
            os.path.join(llvm_dir, get_baseline(b), "CGBuiltin.ii.log"), average_mode
        )
        t = average_times(os.path.join(llvm_dir, b, "CGBuiltin.ii.log"), average_mode)
        results[b] = {"Clang": 100 * (t0 - t) / t0}

    return results


def merge_results(*args):
    results = {}

    for r in args:
        for k, v in r.items():
            if k not in results:
                results[k] = v
            else:
                results[k] |= v

    return results


def generate_plots(results, out_dir):
    # Convert to pandas format (transpose)

    tests = set()
    for b, tt in results.items():
        tests |= tt.keys()

    tests = sorted(tests)
    builds = sorted(results.keys())

    data = {}
    for t in tests:
        data[t] = [results[b].get(t, DEFAULT_VALUE) for b in builds]

    df = pd.DataFrame(data, columns=tests, index=builds)

    # Plot

    df.plot.bar(figsize=(15, 8))
    plt.show()
    plt.savefig(os.path.join(out_dir, "plot.jpeg"))


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Generate C++ benchmarks plots",
        formatter_class=Formatter,
        epilog=f"""\
Examples:
  $ {ME} --pts-dir tmp/PTS/ --ffmpeg-dir tmp/ffmpeg-bench/results/ --llvm-dir tmp/llvm-bench/results StackProtector Fortify2 Fortify3 Bounds ObjectSize HardenedSTL
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
        "--average-mode",
        choices=["median", "mean", "min"],
        default="median",
        help="how to average data",
    )
    parser.add_argument(
        "--tmp-dir",
        help="Path to store temporary files",
    )
    parser.add_argument(
        "--pts-dir",
        help="Path to PTS results",
    )
    parser.add_argument(
        "--ffmpeg-dir",
        help="Path to ffmpeg-bench results",
    )
    parser.add_argument(
        "--llvm-dir",
        help="Path to llvm-bench results",
    )
    parser.add_argument(
        "builds",
        nargs=argparse.REMAINDER,
        default=[],
        help="List of builds to plot (e.g. StackProtector Fortify2 Fortify3)",
    )

    args = parser.parse_args()

    if not any([args.pts_dir, args.ffmpeg_dir, args.llvm_dir]):
        error("at least one of --pts-dir, --ffmpeg-dir and --llvm-dir needed")

    if args.tmp_dir is not None:
        tmp_dir = args.tmp_dir
    else:
        tmp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(tmp_dir))

    results = []

    if args.pts_dir is not None:
        pts_results = collect_pts_results(
            args.builds, args.pts_dir, os.path.join(tmp_dir, "PTS"), args.average_mode
        )
        results.append(pts_results)

    if args.ffmpeg_dir is not None:
        ffmpeg_results = collect_ffmpeg_results(
            args.builds,
            args.ffmpeg_dir,
            os.path.join(tmp_dir, "ffmpeg"),
            args.average_mode,
        )
        results.append(ffmpeg_results)

    if args.llvm_dir is not None:
        llvm_results = collect_llvm_results(
            args.builds, args.llvm_dir, os.path.join(tmp_dir, "llvm"), args.average_mode
        )
        results.append(llvm_results)

    results = merge_results(*results)

    generate_plots(results, args.o)

    return 0


if __name__ == "__main__":
    sys.exit(main())
