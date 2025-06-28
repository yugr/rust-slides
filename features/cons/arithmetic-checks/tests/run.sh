#!/bin/sh

set -eu
set -x

RUSTFLAGS='-O -Ctarget-cpu=native --crate-type=rlib'
#RUSTFLAGS="$RUSTFLAGS -Zsaturating-float-casts=off"
#RUSTFLAGS="$RUSTFLAGS -C overflow-checks=on"

rustc $RUSTFLAGS test.rs
objdump -rd libtest.rlib > test.d
