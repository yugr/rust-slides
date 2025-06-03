#!/bin/sh

set -eu
set -x

rm -f *.d *.s

RUSTFLAGS='--crate-type=rlib -O -C target-cpu=native'

rustc $RUSTFLAGS --emit=asm repro.rs
cat repro.s | c++filt > repro.f.s

rustc $RUSTFLAGS repro.rs
objdump -rd librepro.rlib | c++filt > repro.d
