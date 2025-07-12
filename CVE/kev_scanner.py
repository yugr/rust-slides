#!/usr/bin/env python3

# Scanner of KEVs from https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
#
# Problem with CVEs is that they are often attributed to consequence
# rather than root cause CWE

import argparse
import bs4
import json
import os
import sys
import re


me = os.path.basename(__file__)


def warn(msg):
    """
    Print nicely-formatted warning message.
    """
    sys.stderr.write(f"{me}: warning: {msg}\n")


def error(msg):
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


# TODO: moar categories from https://cwe.mitre.org/data/definitions/699.html ?
CATEGORIES = {
    "Memory Overflow": [
        # Memory Buffer Errors: https://cwe.mitre.org/data/definitions/1218.html (only relevant)
        120, 124, 125, 131, 786, 787, 788, 805,
        # Results of /overflow|underflow|buffer/ search
        119, 121, 122, 126, 127, 680, 806,
        # Pointer Issues: https://cwe.mitre.org/data/definitions/465.html (only relevant)
        466, 468, 469, 823,
    ],
    # https://cwe.mitre.org/data/definitions/189.html (only relevant)
    "Integer Overflow": [
        # Numeric Errors
        1182, 128, 190, 191, 369, 681, 839, 1335,
        # CWE-681: Incorrect Conversion between Numeric Types
        192, 194, 195, 196, 197,
        # Not sure why these are missing
        680,
    ],
    "Stack Overflow": [
        # Hand-picked
        121,
    ],
    "Heap Errors": [
        # Hand-picked
        122, 244, 415, 416, 590, 761,
    ],
    "Uninitialized": [
        # Hand-picked (908 is too abstract but many CVEs use it)
        456, 457, 824, 908,
    ],
}


def main():
    CATEGORIES["Memory Errors"] = list(set(CATEGORIES["Memory Overflow"]) | set(CATEGORIES["Heap Errors"]))

    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="CVE scanner", formatter_class=Formatter
    )
    parser.add_argument("kev_file", help="Path to known_exploited_vulnerabilities.json")
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=2024,
        help="which year to consider",
    )

    args = parser.parse_args()

    with open(args.kev_file) as f:
        j = json.load(f)

    hist = {}

    for v in j["vulnerabilities"]:
        if args.year != int(v["dateAdded"].split("-")[0]):
            continue
        for cwe_id in v["cwes"]:
            m = re.match(r"^CWE-([0-9]+)$", cwe_id)
            error_if(m is None, f"failed to parse CWE '{cwe_id}'")
            cwe_id = int(m[1])
            hist[cwe_id] = hist.get(cwe_id, 0) + 1

    for name, cwe_ids in sorted(CATEGORIES.items()):
        count = 0
        for cwe_id in cwe_ids:
            count += hist.get(cwe_id, 0)
        print(f"{count} {name}")

    total = sum(hist.values())
    print(f"{total} Total")

    return 0


if __name__ == "__main__":
    sys.exit(main())
