#!/bin/sh

# Script to report total effort for material analysis.

set -eu

cd $(dirname $0)

s=0

for m in `grep DONE materials.md | grep -o '[0-9]\+m' | sed -e 's/m//'`; do
  s=$((s+m))
done
s=$(((s + 59) / 60))

for h in `grep DONE materials.md | grep -o '[0-9]\+h' | tr -d 'h'`; do
  s=$((s + h))
done

done=$(grep -c 'Status:.*\(DONE\|wontfix\|duplicate\|postponed\)' materials.md)
all=$(grep -c Status: materials.md)

echo "$((100 * done / all))% ($done/$all) done (spent $(((s + 7) / 8)) man-days)"
