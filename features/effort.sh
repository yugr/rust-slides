#!/bin/sh

# Script to report total effort for material analysis.

set -eu

cd $(dirname $0)

hours=0

for a in `find -name analysis.md`; do
  grep -q '^Effort:' $a || continue
  tmp=$(cat $a | sed -ne '/^Effort:/{ s/^Effort: \+\([0-9.]\+\) *\([a-z]\).*/\1 \2/; p }')
  num=${tmp% *}
  dim=${tmp#* }
  if test $dim != 'h'; then
    echo "Unexpected effort dimension in $a: $dim" >&2
    exit 1
  fi
  hours=$(echo "$hours + $num" | bc -l)
done

weeks=$(echo "$hours / 8 / 5" | bc -l)

echo "$weeks man-weeks"
