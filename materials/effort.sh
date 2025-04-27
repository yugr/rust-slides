#!/bin/sh

set -eu

cd $(dirname $0)

s=0

for m in `grep DONE materials.md | grep -o '[0-9]\+m' | sed -e 's/m//'`; do
  s=$((s+m))
done
s=$((s / 60))

for h in `grep DONE materials.md | grep -o '[0-9]\+h' | tr -d 'h'`; do
  s=$((s + h))
done

echo "Spent $(((s + 7) / 8)) workdays"
