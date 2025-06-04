#!/bin/sh

set -eu
set -x

rm -f *.d *.s

RUSTFLAGS='--crate-type=rlib -O'
#RUSTFLAGS="$RUSTFLAGS -C codegen-units=1'

rustc $RUSTFLAGS --emit=asm test.rs
cat test.s | c++filt > test.f.s

rustc $RUSTFLAGS test.rs
objdump -rd libtest.rlib | c++filt > test.d
