#!/bin/sh

set -eu
set -x

rm -f *.bc *.ll *.o *.rlib *.out

TC=baseline
DIS=$HOME/src/rust/rust/build/x86_64-unknown-linux-gnu/ci-llvm/bin/llvm-dis

errors=0

for t in *.rs; do
  stem=$(basename $t | sed 's/\..*//')

  # Check no reports by default

  rm -f *.bc
  rustc +$TC --crate-type=rlib -O -Csave-temps $t
  ../Count $stem.*.0.rcgu.bc > $stem.out
  if ! diff /dev/null $stem.out; then
    echo >&2 "$t: unexpected output with disabled checks"
    errors=$((errors + 1))
  fi

  # Check match if overflows enabled
  rm -f *.bc
  rustc +$TC --crate-type=rlib -O -Csave-temps -Coverflow-checks=on $t
  ../Count $stem.*.0.rcgu.bc > $stem.out
  if ! diff $stem.ref $stem.out; then
    echo >&2 "$t: mismatched output with enabled checks"
    errors=$((errors + 1))
  fi

done

if test $errors = 0; then
  echo SUCCESS
else
  echo FAIL
fi

exit $errors
