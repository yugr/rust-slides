#!/usr/bin/env python3

# Comparator of collected benchmark results.

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


def compare_runtimes(tests, name, lhs, rhs, average_mode):
    result = 1

    for test in tests:
        lhs_value = float(lhs[test]["avg"][0])
        lhs_dim = lhs[test]["avg"][1]

        rhs_value = float(rhs[test]["avg"][0])
        rhs_dim = rhs[test]["avg"][1]

        lhs_mult, rhs_mult = join(lhs_dim, rhs_dim)
        lhs_value *= lhs_mult
        rhs_value *= rhs_mult

        if average_mode == "geomean":
            result *= rhs_value / lhs_value
        elif average_mode == "min":
            result = min(result, rhs_value / lhs_value)
        else:
            assert average_mode == "max"
            result = max(result, rhs_value / lhs_value)

    if average_mode == "geomean":
        result = (1 - pow(result, 1 / len(tests))) * 100
    else:
        result = (1 - result) * 100

    print(f"{name}: {result:+.1f}%")


def compare_sizes(tests, name, lhs, rhs, average_mode):
    results = {}

    for test in tests:
        for typ, lhs_value in sorted(lhs[test].items()):
            rhs_value = rhs[test][typ]
            if lhs_value != rhs_value:  # Handle zeros
                if average_mode == "geomean":
                    results[typ] = results.get(typ, 1) * rhs_value / lhs_value
                elif average_mode == "min":
                    results[typ] = min(
                        results.get(typ, sys.float_info.max), rhs_value / lhs_value
                    )
                else:
                    assert average_mode == "max"
                    results[typ] = max(
                        results.get(typ, sys.float_info.min), rhs_value / lhs_value
                    )
            else:
                results[typ] = results.get(typ, 1)

    for typ, result in sorted(results.items()):
        if average_mode == "geomean":
            result = (1 - pow(result, 1 / len(tests))) * 100
        else:
            result = (1 - result) * 100
        print(f"{name} {typ}: {result:+.1f}%")


def compare_jsons(lhs, rhs, average_mode, ignore_missing):
    """Compares two .json files with benchmark results."""

    with open(lhs) as f:
        lhs_json = json.load(f)

    with open(rhs) as f:
        rhs_json = json.load(f)

    lhs_tests = set(lhs_json.keys())
    rhs_tests = set(rhs_json.keys())

    if lhs_tests - rhs_tests:
        names = ", ".join(f"'{t}'" for t in sorted(lhs_tests - rhs_tests))
        warn(f"tests {names} are missing in {rhs}")

    if rhs_tests - lhs_tests:
        names = ", ".join(f"'{t}'" for t in sorted(rhs_tests - lhs_tests))
        warn(f"tests {names} are missing in {lhs}")

    if lhs_tests != rhs_tests:
        if not ignore_missing:
            return
        for name in lhs_tests ^ rhs_tests:
            if name in lhs_json:
                del lhs_json[name]
            if name in rhs_json:
                del rhs_json[name]
        lhs_tests = lhs_tests & rhs_tests

    if not lhs_tests:
        return

    if lhs.name.endswith("_sizes.json"):
        compare_sizes(lhs_tests, lhs.name, lhs_json, rhs_json, average_mode)
    else:
        compare_runtimes(lhs_tests, lhs.name, lhs_json, rhs_json, average_mode)


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Simple result comparator", formatter_class=Formatter
    )
    parser.add_argument(
        "--type",
        choices=["avg", "lb", "ub"],
        default="avg",
        help="Which measurement to compare",
    )
    parser.add_argument(
        "--average-mode",
        # Note that mean and median DO NOT MAKE SENSE for ratios
        # ("How to not lie with statistics: The correct way to
        # summarize benchmark results")
        choices=["min", "max", "geomean"],
        default="geomean",
        help="How to average benches within single test",
    )
    parser.add_argument(
        "--ignore-missing",
        action="store_true",
        default=False,
        help="Ignore tests with some testcases missing",
    )
    parser.add_argument(
        "LHS",
        help="Path to baseline results",
    )
    parser.add_argument(
        "RHS",
        help="Path to compared results",
    )
    # TODO: option to compare lb/ub ?

    args = parser.parse_args()

    lhs = Path(args.LHS).absolute()
    rhs = Path(args.RHS).absolute()

    error_if(not lhs.exists(), f"directory '{lhs}' does not exist")
    error_if(not rhs.exists(), f"directory '{rhs}' does not exist")

    lhs_jsons = glob.glob(str(lhs / "*.json"))
    rhs_jsons = glob.glob(str(rhs / "*.json"))

    lhs_basenames = set(map(os.path.basename, lhs_jsons))
    rhs_basenames = set(map(os.path.basename, rhs_jsons))

    if lhs_basenames - rhs_basenames:
        names = ", ".join(sorted(lhs_basenames - rhs_basenames))
        warn(f"some results are present only in {lhs}: {names}")

    if rhs_basenames - lhs_basenames:
        names = ", ".join(sorted(rhs_basenames - lhs_basenames))
        warn(f"some results are present only in {rhs}: {names}")

    json_files = sorted(lhs_basenames & rhs_basenames)

    if not json_files:
        error(f"no common .json files found")

    for json_file in json_files:
        compare_jsons(
            lhs / json_file, rhs / json_file, args.average_mode, args.ignore_missing
        )


if __name__ == "__main__":
    main()
