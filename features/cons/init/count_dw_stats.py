#!/usr/bin/python3

import re
import sys

dead = 0
total = 0

for line in sys.stdin.readlines():
    m = re.search(r'Detected .* dead writes \(([0-9]+) out of ([0-9]+) total\)', line)
    if m is not None:
        dead += int(m.group(1))
        total += int(m.group(2))

rate = int(100 * dead  / total)
print(f"{rate}% ({dead} out of {total})")
