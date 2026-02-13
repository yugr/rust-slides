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
    parser.add_argument(
        "--average-mode",
        choices=["mean", "median", "min"],
        help="averaging method",
        default="mean",
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

    lines = [line.rstrip("\r\n") for line in lines]
    lines.reverse()

    while lines:
        line = lines.pop()

        if line == "The following tests failed to properly run:":
            continue

        # We look for block like this:
        #
        # Botan 2.17.3:
        #     pts/botan-1.6.0 [Test: KASUMI]
        #     Test 1 of 6
        #     Estimated Trial Run Count:    3
        #     Estimated Test Run-Time:      6 Minutes
        #     Estimated Time To Completion: 33 Minutes [11:39 UTC]
        #     Started Run 1 @ 11:07:34
        #     Started Run 2 @ 11:08:09
        #     Started Run 3 @ 11:08:43
        #
        #     Test: KASUMI:
        #         56.423
        #         56.442
        #         56.436
        #
        #     Average: 56.434 MiB/s
        #     Deviation: 0.02%

        m = re.match(r"^([^ ].*):$", line)
        if m is None:
            continue

        test = m[1].replace(" ", "-")

        while lines and lines[-1] and lines[-1].startswith(" "):
            lines.pop()

        if not lines or lines[-1]:
            continue

        lines.pop()  # Empty

        test_case_line = lines.pop()
        m = re.match(r"^    (.*):", test_case_line)
        if m is None:
            continue

        test_case = m[1]

        data = []
        while lines and lines[-1]:
            data_line = lines.pop()
            data.append(float(data_line.strip()))

        if not lines:
            continue

        lines.pop()  # Empty

        #     Average: 62021.0 Requests Per Second
        avg_line = lines.pop()
        m = re.match(r"^ *Average: +([0-9.]+) (.*)", avg_line)
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
                N = 1e9
                dim = "ns"
            elif num > 1e5:
                N = 1e6
                dim = "us"
            elif num > 1e2:
                N = 1e3
                dim = "ms"
            else:
                N = 1
                dim = "s"
            num = N / num
            data = [N / d for d in data]
        elif dim == "Seconds":
            dim = "s"
        else:
            error(f"unknown dimension '{dim}'")

        #     Deviation: 0.19%
        std_line = lines.pop()
        m = re.match(r"^ *Deviation: +([0-9.]+)%", std_line)
        if m is not None and float(m[1]) > 1:
            warn(f"skipping noisy test case '{test_case}' in '{test}'")
            continue

        if args.average_mode == "min":
            val = min(data)
        elif args.average_mode == "mean":
            val = sum(data) / len(data)
        else:
            assert args.average_mode == "median"
            val = data[len(data) // 2]

        results.setdefault(test, {})[test_case] = {
            "avg": [val, dim],
        }

    os.makedirs(args.output, exist_ok=True)
    for test, cases in results.items():
        with open(os.path.join(args.output, test + ".json"), "w") as f:
            f.write(json.dumps(cases, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
