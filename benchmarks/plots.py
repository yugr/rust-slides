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


def collect_results(builds, paths, baseline, tmp_dir):
    all_builds = set(builds)
    all_builds.add(baseline)

    compare = os.path.join(os.path.dirname(__file__), "compare.py")
    combine = os.path.join(os.path.dirname(__file__), "combine.py")

    out_dir = os.path.join(tmp_dir, "combined")

    for b in all_builds:
        dd = []
        for d in paths:
            if os.path.exists(os.path.join(d, b)):
                dd.append(os.path.join(d, b))

        run([combine, "--ignore-missing", "-o", os.path.join(out_dir, b)] + dd)

    results = {}

    for b in builds:
        _, out, _ = run(
            [compare, os.path.join(out_dir, baseline), os.path.join(out_dir, b)]
        )

        build_name = os.path.basename(b.rstrip("/"))

        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue

            # SpacetimeDB_0.json: +0.8%
            # SpacetimeDB_sizes.json rodata: -0.0%
            # SpacetimeDB_sizes.json text: +3.9%
            m = re.match(r"^(.*)(?:_sizes)?\.json(.*): (.*)%$", line)
            error_if(m is None, f"failed to parse compare.py output: {line}")

            name = m[1]
            typ = m[2].strip() or "perf"
            diff = float(m[3])

            results.setdefault(typ, {}).setdefault(build_name, {})[name] = diff

    return results


def generate_plots(results, out_dir):
    for typ, typ_results in results.items():
        x = np.arange(len(typ_results))
        fig, ax = plt.subplots(
            figsize=(5 * (len(typ_results) + 1), 8), layout="constrained"
        )

        colors = {}
        legend_handles = {}
        # something like 12 benchmarks should take up 80% of space between groups
        width = 0.8 / 12
        build_widths = np.zeros(len(typ_results))
        for build_index, build_results in enumerate(typ_results.values()):
            build_widths[build_index] = (len(build_results) - 1) * width
            for bench_index, (bench_name, value) in enumerate(build_results.items()):
                color = colors.setdefault(bench_name, cm.tab20(len(colors) / 20))
                rect = ax.bar(
                    build_index + width * bench_index,
                    value,
                    width,
                    label=bench_name,
                    color=color,
                )
                legend_handles.setdefault(bench_name, rect)
                ax.bar_label(rect, padding=3, fmt="%.1f")

        ax.set_ylabel("% change")
        ax.set_yscale("symlog")
        ax.set_xticks(x + build_widths / 2, typ_results.keys())
        ax.set_ylim(-100, 100)
        ax.legend(ncols=3, handles=legend_handles.values())
        plt.show()
        fig.savefig(os.path.join(out_dir, f"{typ}.png"))


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
  $ {ME} path/to/build1 path/to/build2 ...
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
        "builds",
        nargs=argparse.REMAINDER,
        default=[],
        help="List of builds to plot",
    )

    args = parser.parse_args()

    if args.tmp_dir is not None:
        tmp_dir = os.path.join(args.tmp_dir, "plots")
        shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)
    else:
        tmp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(tmp_dir))

    results = collect_results(args.builds, args.path, args.baseline, tmp_dir)

    generate_plots(results, args.o)

    return 0


if __name__ == "__main__":
    sys.exit(main())
