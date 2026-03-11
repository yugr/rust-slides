#!/usr/bin/env python3

# Combine several collected benchmark results.

from __future__ import annotations

import argparse
import glob
import json
import os.path
from pathlib import Path
import sys

me = os.path.basename(__file__)


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


def join(dims):
    """Align dimensions."""

    dim2deg = dict(s=0, ms=3, us=6, ns=9, ps=12)
    deg2dim = {0: "s", 3: "ms", 6: "us", 9: "ns", 12: "ps"}

    degs = [dim2deg[d] for d in dims]
    max_deg = max(degs)

    mults = []

    for d in degs:
        if d == max_deg:
            m = 1
        else:
            assert d < max_deg
            m = pow(10, max_deg - d)
        mults.append(m)

    return mults, deg2dim[max_deg]


def combine_results(dirs, out, average_mode):
    """Combine results from multiple runs."""

    json_files = set()
    for d in dirs:
        for json_file in glob.glob(str(d / "*.json")):
            json_files.add(os.path.basename(json_file))
    json_files = sorted(json_files)

    for json_file in json_files:
        missing = []
        for d in dirs:
            if not (d / json_file).exists():
                missing.append(d)
        if missing:
            missing = ", ".join(missing)
            warn(f"{json_file} is missing in some directories: {missing}")

    error_if(not json_files, "no .json files found")

    for json_file in json_files:
        res = []
        for d in dirs:
            local_json_file = d / json_file
            if not local_json_file.exists():
                continue
            with open(local_json_file) as f:
                res.append((local_json_file, json.load(f)))

        if json_file.endswith("_sizes.json"):
            local_json_file_0, r_0 = res[0]
            for local_json_file, r in res:
                error_if(r_0 != r, f"files {local_json_file_0} and {local_json_file} do not match")

            with open(out / json_file, "w") as f:
                f.write(json.dumps(res[0][1], indent=4, sort_keys=True))

            continue

        # Performance jsons

        tests = set()
        for _, r in res:
            for test in r.keys():
                tests.add(test)
        tests = sorted(tests)

        for test in tests:
            missing = []
            for filename, r in res:
                if test not in r:
                    missing.append(d)
            if missing:
                missing = ", ".join(missing)
                error(
                    f"test {json_file}/{test} is missing in some directories: {missing}"
                )

        r_new = {}

        for test in tests:
            vals = []
            dims = []
            for _, r in res:
                if test not in r:
                    continue
                val, dim = r[test]["avg"]
                vals.append(float(val))
                dims.append(dim)

            mults, dim = join(dims)
            vals = [val * mult for val, mult in zip(vals, mults)]

            if average_mode == "mean":
                val = sum(vals) / len(vals)
            elif average_mode == "min":
                val = min(vals)
            else:
                assert average_mode == "max"
                val = max(vals)

            r_new[test] = {"avg": [val, dim]}

        with open(out / json_file, "w") as f:
            f.write(json.dumps(r_new, indent=4, sort_keys=True))


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Simple result combiner", formatter_class=Formatter
    )
    parser.add_argument(
        "--average-mode",
        choices=["min", "max", "mean"],
        default="min",
        help="How to average tests across runs",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory for combined results",
    )
    parser.add_argument(
        "--ignore-missing",
        action="store_true",
        default=False,
        help="Ignore tests with some testcases missing",
    )
    parser.add_argument(
        "DIR",
        help="Path to baseline results",
        nargs="+",
        default=[],
    )

    args = parser.parse_args()

    dirs = [Path(d) for d in args.DIR]
    for d in dirs:
        error_if(not d.exists(), f"directory '{d}' does not exist")

    os.makedirs(args.output, exist_ok=True)
    out = Path(args.output)
    for json_file in glob.glob(str(out / "*.json")):
        os.unlink(json_file)

    combine_results(dirs, out, args.average_mode)


if __name__ == "__main__":
    main()
