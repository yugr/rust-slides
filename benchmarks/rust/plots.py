#!/usr/bin/python3

# Plots benchmark results for Rust benchmarks.

import argparse
import atexit
import os
import os.path
import re
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


def collect_results(builds, paths, baseline, tmp_dir):
    all_builds = set(builds)
    all_builds.add(baseline)

    compare = os.path.join(os.path.dirname(__file__), "..", "compare.py")
    combine = os.path.join(os.path.dirname(__file__), "..", "combine.py")

    out_dir = os.path.join(tmp_dir, "combined")

    for b in sorted(all_builds):
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

            if "oxipng" in name:
                # Just too noisy
                continue

            results.setdefault(typ, {}).setdefault(build_name, {})[name] = diff

    return results


def generate_plots(all_results, out_dir, font_size, use_logscale, outside_legend):
    for typ, results in sorted(all_results.items()):
        colorscheme = cm.tab20
        num_colors_in_colorscheme = 20

        minimal_colorbar_heigth = 0.05

        base_horizontal_fig_size = 5
        vertical_fig_size = 8
        x = np.arange(len(results))
        fig, ax = plt.subplots(
            figsize=(base_horizontal_fig_size * (len(results) + 1), vertical_fig_size),
            layout="constrained",
        )

        colors = {}
        legend_handles = {}
        max_bench_count = max(len(data) for data in results.values())
        space_per_build = 0.8
        width = space_per_build / max_bench_count
        build_widths = np.zeros(len(results))
        for build_index, (_, build_results) in enumerate(sorted(results.items())):
            build_widths[build_index] = (len(build_results) - 1) * width
            for bench_index, (bench_name, value) in enumerate(
                sorted(build_results.items())
            ):
                color = colors.setdefault(
                    bench_name, colorscheme(len(colors) / num_colors_in_colorscheme)
                )
                rect = ax.bar(
                    build_index + width * bench_index,
                    (
                        value
                        if abs(value) >= minimal_colorbar_heigth
                        else minimal_colorbar_heigth
                    ),
                    width,
                    label=bench_name,
                    color=color,
                )
                legend_handles.setdefault(bench_name, rect)
                if value != 0:
                    ax.bar_label(rect, padding=3, fmt="%.1f", fontsize=font_size)

        ax.set_ylabel("% change", fontsize=font_size)
        if use_logscale:
            ax.set_yscale("symlog")
        ax.set_xticks(
            x + build_widths / 2,
            results.keys(),
            fontsize=font_size,
        )
        if outside_legend:
            fig.legend(loc="outside right upper", fontsize=font_size)
        else:
            ax.legend(
                ncols=3,
                handles=legend_handles.values(),
                fontsize=font_size,
                loc="outside right upper",
            )
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
  $ {ME} --baseline=baseline build1 build2 ...
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
        "builds",
        nargs=argparse.REMAINDER,
        default=[],
        help="List of builds to plot",
    )
    parser.add_argument(
        "--font-size",
        help="Size of font for plots",
        default=10,
    )
    parser.add_argument(
        "--logscale", "-l", action="store_true", help="Use logscale for y axis"
    )
    parser.add_argument(
        "--outside-legend",
        action=argparse.BooleanOptionalAction,
        help="Put legend to the right of the plot",
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

    results = collect_results(args.builds, args.path, args.baseline, tmp_dir)

    generate_plots(results, args.o, args.font_size, args.logscale, args.outside_legend)

    return 0


if __name__ == "__main__":
    sys.exit(main())
