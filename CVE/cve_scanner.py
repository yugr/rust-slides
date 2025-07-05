#!/usr/bin/env python3

# Scanner of CVEs in https://github.com/CVEProject/cvelistV5
#
# I usually scan only cvelistV5/cves/2024

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


def find_keys(json_data, target_key, results=None):
    if results is None:
        results = []

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == target_key:
                results.append(value)
            else:
                find_keys(value, target_key, results)
    elif isinstance(json_data, list):
        for item in json_data:
            find_keys(item, target_key, results)

    return results


def read_cwe_descs():
    # Download "Comprehensive CWE Dictionary" at https://cwe.mitre.org/data/definitions/2000.html

    with open("2000.html") as f:
        s = bs4.BeautifulSoup(f.read(), "html.parser")

    idx = {}

    for tr in s.find("table", id="Detail").tbody.find_all("tr"):
        tds = tr.find_all("td")
        id = int(tds[2].text.strip())
        desc = tds[3].text.strip()
        idx[id] = desc

    return idx


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
        # Hand-picked
        456, 457, 824,
    ],
}


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="CVE scanner", formatter_class=Formatter
    )
    parser.add_argument("dir", nargs="+", help="Directory with CVEs")

    args = parser.parse_args()

    files = []
    for dir in args.dir:
        for d, _, ff in os.walk(dir):
            files.extend(os.path.join(d, f) for f in ff if re.match(r"CVE-.*\.json", f))

    hist = {}
    fails = []

    for fil in files:
        with open(fil) as f:
            j = json.load(f)

        results = find_keys(j, "problemTypes")
        if not results:
            fails.append(fil)
            continue

        for problem_types in results:
            for problem_type in problem_types:
                for desc in problem_type["descriptions"]:
                    if "cweId" in desc:
                        cwe_id = desc["cweId"]
                        m = re.match(r"CWE-([0-9]+)$", cwe_id)
                        error_if(m is None, f"failed to parse CWE: {cwe_id}")
                        cwe_id = int(m[1])
                        hist[cwe_id] = hist.get(cwe_id, 0) + 1

    cwe_descs = read_cwe_descs()

    print("# CWEs:")
    total = 0
    for cwe_id, count in sorted(hist.items(), key=lambda h: h[1]):
        desc = cwe_descs.get(cwe_id, f"unknown CWE {cwe_id}")
        print(f"{count}: {desc}")
        total += count
    print(f"{total} total\n")

    print("# Categories:")
    for name, cwe_ids in sorted(CATEGORIES.items()):
        count = 0
        for cwe_id in cwe_ids:
            count += hist.get(cwe_id, 0)
        print(f"{count} {name}")

    print(f"Failed to extract CWE from {len(fails)} files (out of {len(files)})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
