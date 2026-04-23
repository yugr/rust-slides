#!/usr/bin/python3

# Plots histogram of speedups (slowdowns) and
# computes common stats for C++ benchmarks.
#
# This is most likely not statistically correct.

import argparse
import atexit
import glob
import json
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
from matplotlib import cm
import numpy as np

ME = os.path.basename(__file__)


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


def join(lhs, rhs):
    """Align dimensions."""

    dim2deg = dict(s=0, ms=3, us=6, ns=9, ps=12)

    lhs_deg = dim2deg[lhs]
    rhs_deg = dim2deg[rhs]

    if lhs_deg == rhs_deg:
        return 1, 1
    elif lhs_deg < rhs_deg:
        return pow(10, rhs_deg - lhs_deg), 1
    else:
        return 1, pow(10, lhs_deg - rhs_deg)


def get_baseline(b):
    return "Libcxx" if b in ("Libcxx", "HardenedSTL") else "Baseline"


def compare_jsons(lhs, rhs, json_name):
    results = {}

    for t, rhs_value in sorted(rhs.items()):
        lhs_value = lhs.get(t)
        if lhs_value is None:
            continue
        rt = rhs[t]

        lhs_value, lhs_dim = lhs_value["avg"]
        rhs_value, rhs_dim = rhs_value["avg"]

        lhs_mult, rhs_mult = join(lhs_dim, rhs_dim)
        lhs_value *= lhs_mult
        rhs_value *= rhs_mult

        results[t] = rhs_value / lhs_value - 1

    return results.values()


def collect_pts_results(build, pts_dir, tmp_dir, average_mode):
    base = get_baseline(build)

    parser = os.path.join(os.path.dirname(__file__), "PTS", "parser.py")
    compare = os.path.join(os.path.dirname(__file__), "..", "compare.py")
    combine = os.path.join(os.path.dirname(__file__), "..", "combine.py")

    for b in [base, build]:
        oo = []
        for i, d in enumerate(pts_dir):
            f = os.path.join(d, b + ".log")
            error_if(not os.path.exists(f), f"PTS result file {f} does not exist")

            o = os.path.join(tmp_dir, f"{b}-{i}")
            oo.append(o)

            run(
                [
                    parser,
                    "--std-threshold",
                    0.5,
                    "--average-mode",
                    average_mode,
                    "-o",
                    o,
                    f,
                ]
            )

            run([combine, "--ignore-missing", "-o", os.path.join(tmp_dir, b)] + oo)

    results = {}

    rhs_jsons = glob.glob(os.path.join(os.path.join(tmp_dir, b), "*.json"))

    for rhs_json in rhs_jsons:
        lhs_json = os.path.join(tmp_dir, base, os.path.basename(rhs_json))
        if not os.path.exists(lhs_json):
            warn(f"{lhs_json} does not exist")
            continue

        name = re.match(r"^(.*).json", os.path.basename(rhs_json))[1]

        with open(lhs_json) as f:
            lhs_json = json.load(f)

        with open(rhs_json) as f:
            rhs_json = json.load(f)

        results[name] = compare_jsons(lhs_json, rhs_json, name)

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


def collect_ffmpeg_results(build, ffmpeg_dir, tmp_dir, average_mode):
    base = get_baseline(build)

    tt = []
    for d in ffmpeg_dir:
        t = average_times(os.path.join(d, base + ".log"), average_mode)
        tt.append(t)
    base_time = min(tt)

    tt = []
    for d in ffmpeg_dir:
        t = average_times(os.path.join(d, build + ".log"), average_mode)
        tt.append(t)
    build_time = min(tt)  # TODO: other cross-run averaging modes

    return [build_time / base_time - 1]


def collect_llvm_results(build, llvm_dir, tmp_dir, average_mode):
    base = get_baseline(build)

    tt = []
    for d in llvm_dir:
        t = average_times(os.path.join(d, base, "CGBuiltin.ii.log"), average_mode)
        tt.append(t)
    base_time = min(tt)

    tt = []
    for d in llvm_dir:
        t = average_times(os.path.join(d, build, "CGBuiltin.ii.log"), average_mode)
        tt.append(t)
    build_time = min(tt)  # TODO: other cross-run averaging modes

    return [build_time / base_time - 1]


# Plot flat histogram of all results
def histogram(results, out_dir):
    # TODO: weight by number of tests in each project ?
    results = [r for rr in results.values() for r in rr]

    results = [100 * r for r in results]

    med = np.median(results)
    print(f"Median speedup: {med:.1f}%")

    m = np.mean(results)
    print(f"Average speedup: {m:.1f}%")

    percentile = 95

    p = np.percentile(results, percentile)
    print(f"p{percentile}: {p:.1f}%")

    counts, bins = np.histogram(results, 50)
    fig, ax = plt.subplots()
    plt.stairs(counts, bins)
    plt.xlim(-20, 20)

    plt.axvline(m, color="k", linestyle="dashed", linewidth=1)
    plt.axvline(p, color="k", linestyle="dashed", linewidth=1)

    min_ylim, max_ylim = plt.ylim()
    plt.text(m * 1.1, max_ylim * 0.9, f"Mean: {m:.1f}")
    plt.text(p * 1.1, max_ylim * 0.8, f"P{percentile}: {p:.1f}")

    ax.set_xlabel("% change")

    fig.savefig(os.path.join(out_dir, f"hist.png"))


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Plot histogram of C++ speedups (or slowdowns)",
        formatter_class=Formatter,
        epilog=f"""\
Examples:
  $ {ME} --pts-dir tmp/PTS/ --ffmpeg-dir tmp/ffmpeg-bench/results/ --llvm-dir tmp/llvm-bench/results HardenedCpp
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
        action="append",
        default=[],
    )
    parser.add_argument(
        "--ffmpeg-dir",
        help="Path to ffmpeg-bench results",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--llvm-dir",
        help="Path to llvm-bench results",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--font-size",
        help="Size of font for plots",
        default=10,
    )
    parser.add_argument(
        "build",
        help="Build to compare",
    )

    args = parser.parse_args()

    if not any([args.pts_dir, args.ffmpeg_dir, args.llvm_dir]):
        error("at least one of --pts-dir, --ffmpeg-dir and --llvm-dir needed")

    if args.tmp_dir is not None:
        tmp_dir = os.path.join(args.tmp_dir, "plots")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)
    else:
        tmp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(tmp_dir))

    results = {}

    if args.pts_dir:
        pts_results = collect_pts_results(
            args.build, args.pts_dir, os.path.join(tmp_dir, "PTS"), args.average_mode
        )
        results.update(pts_results)

    if args.ffmpeg_dir:
        results["ffmpeg"] = collect_ffmpeg_results(
            args.build,
            args.ffmpeg_dir,
            os.path.join(tmp_dir, "ffmpeg"),
            args.average_mode,
        )

    if args.llvm_dir:
        results["Clang"] = collect_llvm_results(
            args.build, args.llvm_dir, os.path.join(tmp_dir, "llvm"), args.average_mode
        )

    histogram(results, args.o)

    return 0


if __name__ == "__main__":
    sys.exit(main())
