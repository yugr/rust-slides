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
    def deg(dim):
        if dim == "s":
            return 0
        elif dim == "ms":
            return 3
        elif dim == "us":
            return 6
        elif dim == "ns":
            return 9
        elif dim == "ps":
            return 12
        assert False, f"unknown dimension: {dim}"

    lhs_deg = deg(lhs)
    rhs_deg = deg(rhs)

    if lhs_deg == rhs_deg:
        return 1, 1
    elif lhs_deg < rhs_deg:
        return pow(10, rhs_deg - lhs_deg), 1
    else:
        return 1, pow(10, lhs_deg - rhs_deg)


def compare_runtimes(tests, name, lhs, rhs):
    geomean = 1

    for test in tests:
        lhs_value = float(lhs[test]["avg"][0])
        lhs_dim = lhs[test]["avg"][1]

        rhs_value = float(rhs[test]["avg"][0])
        rhs_dim = rhs[test]["avg"][1]

        lhs_mult, rhs_mult = join(lhs_dim, rhs_dim)
        lhs_value *= lhs_mult
        rhs_value *= rhs_mult

        geomean *= rhs_value / lhs_value

    geomean = (1 - pow(geomean, 1 / len(tests))) * 100

    print(f"{name}: {geomean:+.1f}%")


def compare_sizes(tests, name, lhs, rhs):
    geomeans = {}

    for test in tests:
        for typ, lhs_value in sorted(lhs[test].items()):
            rhs_value = rhs[test][typ]
            if lhs_value != rhs_value:
                geomeans[typ] = geomeans.get(typ, 1) * lhs_value / rhs_value
            else:
                geomeans[typ] = geomeans.get(typ, 1)

    for typ, geomean in sorted(geomeans.items()):
        geomean = (1 - pow(geomean, 1 / len(tests))) * 100
        print(f"{name} {typ}: {geomean:+.1f}%")


def compare_jsons(lhs, rhs):
    """Compares two .json files with benchmark results."""

    with open(lhs) as f:
        lhs_json = json.load(f)

    with open(rhs) as f:
        rhs_json = json.load(f)

    lhs_tests = set(sorted(lhs_json.keys()))
    rhs_tests = set(sorted(rhs_json.keys()))

    if lhs_tests - rhs_tests:
        names = ", ".join(lhs_tests - rhs_tests)
        warn(f"tests {names} are missing in {rhs}")

    if rhs_tests - lhs_tests:
        names = ", ".join(rhs_tests - lhs_tests)
        warn(f"tests {names} are missing in {lhs}")

    if lhs.name.endswith("_sizes.json"):
        compare_sizes(lhs_tests, lhs.name, lhs_json, rhs_json)
    else:
        compare_runtimes(lhs_tests, lhs.name, lhs_json, rhs_json)


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
        compare_jsons(lhs / json_file, rhs / json_file)


if __name__ == "__main__":
    main()
