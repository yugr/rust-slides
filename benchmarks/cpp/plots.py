#!/usr/bin/python3

# Plots benchmark results for C++ benchmarks (Clang, ffmpeg, PTS).

import argparse
import atexit
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


def get_baseline(b):
    return "Libcxx" if b in ("Libcxx", "HardenedSTL", "HardenedCpp") else "Baseline"


def collect_pts_results(builds, pts_dir, tmp_dir, average_mode, baseline):
    all_builds = set(builds)
    if baseline is None:
        for b in builds:
            all_builds.add(get_baseline(b))
    else:
        all_builds.add(baseline)

    parser = os.path.join(os.path.dirname(__file__), "PTS", "parser.py")
    compare = os.path.join(os.path.dirname(__file__), "..", "compare.py")
    combine = os.path.join(os.path.dirname(__file__), "..", "combine.py")

    for b in sorted(all_builds):
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

    for b in builds:
        base = os.path.join(tmp_dir, baseline or get_baseline(b))
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
            val = 0 if abs(val) < 1 else val
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


def collect_ffmpeg_results(builds, ffmpeg_dir, tmp_dir, average_mode, baseline):
    all_builds = set(builds)
    if baseline is None:
        for b in builds:
            all_builds.add(get_baseline(b))
    else:
        all_builds.add(baseline)

    times = {}
    for b in sorted(all_builds):
        tt = []
        for d in ffmpeg_dir:
            t = average_times(os.path.join(d, b + ".log"), average_mode)
            tt.append(t)
        times[b] = min(tt)  # TODO: other cross-run averaging modes

    results = {}
    for b in builds:
        t0 = times[baseline or get_baseline(b)]
        t = times[b]
        results[b] = {"ffmpeg": 100 * (t0 - t) / t0}

    return results


def collect_llvm_results(builds, llvm_dir, tmp_dir, average_mode, baseline):
    all_builds = set(builds)
    if baseline is None:
        for b in builds:
            all_builds.add(get_baseline(b))
    else:
        all_builds.add(baseline)

    times = {}
    for b in sorted(all_builds):
        tt = []
        for d in llvm_dir:
            t = average_times(os.path.join(d, b, "CGBuiltin.ii.log"), average_mode)
            tt.append(t)
        times[b] = min(tt)  # TODO: other cross-run averaging modes

    results = {}
    for b in builds:
        t0 = times[baseline or get_baseline(b)]
        t = times[b]
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


def generate_plots(results, out_dir, font_size, use_logscale, outside_legend):
    sym_names = dict(
        StackProtector="-fstack-protector-strong",
        Fortify2="-D_FORTIFY_SOURCE=2",
        Fortify3="-D_FORTIFY_SOURCE=3",
        Bounds="-fsanitize=bounds",
        ObjectSize="-fsanitize=object-size",
        HardenedSTL="Hardened STL (libc++)",
        HardenedCpp="Hardened C++ (libc++)",
        AutoInit="Initialization (stack)",
        AutoInitWithHeap="Initialization (stack+heap)",
        IOF="-fsanitize=signed-integer-overflow",
        StackClash="Stack Clashing",
        FastMath="-ffast-math",
    )

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
    # something like 12 benchmarks should take up 80% of space between groups
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
                value if value != 0 else minimal_colorbar_heigth,
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
        [sym_names[build] for build in results.keys()],
        fontsize=font_size,
    )
    # ax.set_ylim(-100, 100)
    if outside_legend:
        fig.legend(loc="outside right upper", fontsize=font_size)
    else:
        ax.legend(
            ncols=3,
            handles=legend_handles.values(),
            fontsize=font_size,
        )
    plt.show()
    fig.savefig(os.path.join(out_dir, "plot.png"))


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
        "--baseline",
        help="Build to compare against",
    )
    parser.add_argument(
        "--font-size",
        help="Size of font for plots",
        default=10,
    )
    parser.add_argument(
        "--logscale",
        "-l",
        action="store_true",
        help="Use logscale for y axis",
    )
    parser.add_argument(
        "--outside-legend",
        action=argparse.BooleanOptionalAction,
        help="Put legend to the right of the plot",
    )
    parser.add_argument(
        "builds",
        nargs="+",
        default=[],
        help="List of builds to plot (e.g. StackProtector Fortify2 Fortify3)",
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

    results = []

    if args.pts_dir:
        pts_results = collect_pts_results(
            args.builds,
            args.pts_dir,
            os.path.join(tmp_dir, "PTS"),
            args.average_mode,
            args.baseline,
        )
        results.append(pts_results)

    if args.ffmpeg_dir:
        ffmpeg_results = collect_ffmpeg_results(
            args.builds,
            args.ffmpeg_dir,
            os.path.join(tmp_dir, "ffmpeg"),
            args.average_mode,
            args.baseline,
        )
        results.append(ffmpeg_results)

    if args.llvm_dir:
        llvm_results = collect_llvm_results(
            args.builds,
            args.llvm_dir,
            os.path.join(tmp_dir, "llvm"),
            args.average_mode,
            args.baseline,
        )
        results.append(llvm_results)

    results = merge_results(*results)

    generate_plots(results, args.o, args.font_size, args.logscale, args.outside_legend)

    return 0


if __name__ == "__main__":
    sys.exit(main())
