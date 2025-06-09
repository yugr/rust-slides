#!/bin/sh

set -eu
set -x

rm -f *.bc *.ll *.o *.rlib *.out

TC=baseline
DIS=$HOME/src/rust/$TC/build/x86_64-unknown-linux-gnu/ci-llvm/bin/llvm-dis

errors=0

for t in *.rs; do
  stem=$(basename $t | sed 's/\..*//')
  rustc +$TC --crate-type=rlib -O -C target-cpu=native -C save-temps $t
  $DIS $stem.*.0.rcgu.bc -o $stem.ll
  ../CountLoops $stem.*.0.rcgu.bc > $stem.out
  if diff $stem.out $stem.ref; then
    echo >&2 "Unexpected difference for $t"
    errors=$((errors + 1))
  fi
done

exit $errors
