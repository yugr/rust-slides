#!/usr/bin/python3

# Plots histogram of speedups (slowdowns) and computes common stats
# for Rust benchmarks. This is most likely not statistically correct.

import argparse
import atexit
import glob
import json
import os
import os.path
import shutil
import subprocess
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


def compare_jsons(lhs, rhs):
    results = []

    for t, rhs_value in sorted(rhs.items()):
        lhs_value = lhs[t]
        rt = rhs[t]

        lhs_value, lhs_dim = lhs_value["avg"]
        rhs_value, rhs_dim = rhs_value["avg"]

        lhs_mult, rhs_mult = join(lhs_dim, rhs_dim)
        lhs_value *= lhs_mult
        rhs_value *= rhs_mult

        results.append(1 - rhs_value / lhs_value)

    return results


def collect_results(lhs, rhs, paths, tmp_dir):
    compare = os.path.join(os.path.dirname(__file__), "..", "compare.py")
    combine = os.path.join(os.path.dirname(__file__), "..", "combine.py")

    out_dir = os.path.join(tmp_dir, "combined")

    for b in [lhs, rhs]:
        dd = []
        for d in paths:
            if os.path.exists(os.path.join(d, b)):
                dd.append(os.path.join(d, b))

        run([combine, "--ignore-missing", "-o", os.path.join(out_dir, b)] + dd)

    results = []

    # TODO: support sizes too
    rhs_jsons = glob.glob(os.path.join(os.path.join(out_dir, rhs), "*_0.json"))

    for rhs_json in rhs_jsons:
        lhs_json = os.path.join(out_dir, lhs, os.path.basename(rhs_json))
        if not os.path.exists(lhs_json):
            warn(f"{lhs_json} does not exist")
            continue

        with open(lhs_json) as f:
            lhs_json = json.load(f)

        with open(rhs_json) as f:
            rhs_json = json.load(f)

        results.extend(compare_jsons(lhs_json, rhs_json))

    return results


def generate_plots(results, out_dir):
    results = [100 * r for r in results]

    m = np.mean(results)
    print(f"Average deviation: {m:.1f}%")

    p = np.percentile(results, 95)
    print(f"p95: {p:.1f}%")

    counts, bins = np.histogram(results, 100)
    fig, ax = plt.subplots()
    plt.stairs(counts, bins)
    plt.xlim(-20, 20)
    fig.savefig(os.path.join(out_dir, f"hist.png"))


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Plot histogram of Rust speedups (or slowdowns)",
        formatter_class=Formatter,
        epilog=f"""\
Examples:
  $ {ME} --baseline=baseline bounds
""",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Print diagnostic info (can be specified more than once)",
        action="count",
        default=0,
    )
    parser.add_argument("-o", help="Path to store results", default=".")
    parser.add_argument(
        "--baseline",
        help="Name of baseline build to compare against",
        default="baseline",
    )
    parser.add_argument(
        "--path",
        help="Path to builds",
        action="append",
        default=[],
        required=True,
    )
    parser.add_argument(
        "--tmp-dir",
        help="Path to store temporary files",
    )
    parser.add_argument(
        "build",
        help="Build to compare",
    )

    args = parser.parse_args()

    if args.tmp_dir is not None:
        tmp_dir = os.path.join(args.tmp_dir, "plots")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)
    else:
        tmp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(tmp_dir))

    results = collect_results(args.baseline, args.build, args.path, tmp_dir)

    generate_plots(results, args.o)

    return 0


if __name__ == "__main__":
    sys.exit(main())
