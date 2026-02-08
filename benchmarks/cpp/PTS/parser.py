#!/usr/bin/env python3

# Convert Phoronix output to json format expected by compare.py.

import argparse
import glob
import json
import os
import os.path
import re
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


def main():
    class Formatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        description="Parser of Phoronix logs", formatter_class=Formatter
    )
    parser.add_argument("-o", "--output", help="where to place jsons", default=".")
    parser.add_argument(
        "-v",
        "--verbose",
        help="print build logs",
        action="count",
        default=0,
    )
    parser.add_argument(
        "LOG",
        nargs="?",
        default=None,
        help="Log to parse (default stdin)",
    )

    args = parser.parse_args()

    if args.LOG is None:
        lines = sys.stdin.readlines()
    else:
        with open(args.LOG, "r") as f:
            lines = f.readlines()

    for f in glob.glob(os.path.join(args.output, "*.json")):
        os.unlink(f)

    results = {}
    current_test = current_testcase = None
    blacklist = {}

    for line in lines:
        # Installed:     pts/apache-3.0.0
        m = re.match(r"^ *Installed: +(.*)", line)
        if m is not None:
            current_test = m[1]
            results.setdefault(current_test, {})
            continue

        # pts/apache-3.0.0 [Concurrent Requests: 4]
        if current_test is not None and line.lstrip().startswith(current_test):
            m = re.match(r".*\[(.*)\]", line)
            if m is None:
                current_testcase = "MAIN"
            else:
                current_testcase = m[1]
            if current_testcase in results[current_test]:
                error(
                    f"multiple instances of '{current_testcase}' testcase in '{current_test}' test"
                )
            results[current_test][current_testcase] = {}
            continue

        #     Average: 62021.0 Requests Per Second
        m = re.match(r"^ *Average: +([0-9.]+) (.*)", line)
        if m is not None:
            assert current_test is not None
            assert current_testcase is not None

            num, dim = m.groups()
            num = float(num)

            if (
                dim.endswith("/s")
                or dim.endswith("/Sec")
                or dim.endswith("Per Second")
                or dim.endswith("Score")
                or dim.endswith("flops")
            ):
                # Convert rates to readable times
                if num > 1e8:
                    num = 1e9 / num
                    dim = "ns"
                elif num > 1e5:
                    num = 1e6 / num
                    dim = "us"
                elif num > 1e2:
                    num = 1e3 / num
                    dim = "ms"
                else:
                    num = 1 / num
                    dim = "s"
            elif dim == "Seconds":
                dim = "s"
            else:
                error(f"unknown dimension '{dim}'")

            results[current_test][current_testcase]["avg"] = [num, dim]

        #     Deviation: 0.19%
        m = re.match(r"^ *Deviation: +([0-9.]+)%", line)
        if m is not None:
            assert current_test is not None
            assert current_testcase is not None
            if float(m[1]) > 1:
                blacklist.setdefault(current_test, set()).add(current_testcase)

    os.makedirs(args.output, exist_ok=True)
    for test, cases in results.items():
        for case, vals in sorted(cases.items()):
            if not vals:
                warn(f"skipping empty test case '{case}' in '{test}'")
                del cases[case]
            if test in blacklist and case in blacklist[test]:
                warn(f"skipping noisy test case '{case}' in '{test}'")
                del cases[case]
        if not cases:
            warn(f"no test cases for '{test}'")
            continue
        test = re.sub(r".*\/", "", test)
        with open(os.path.join(args.output, test + ".json"), "w") as f:
            f.write(json.dumps(cases, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
