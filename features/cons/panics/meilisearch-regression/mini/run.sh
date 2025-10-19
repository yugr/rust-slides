#!/bin/sh

set -eu
set -x

rm -f *.s *.bc *.ll

RUSTFLAGS='-O -Copt-level=3 -Ccodegen-units=1 --crate-type=rlib --emit=asm'
#RUSTFLAGS="$RUSTFLAGS -Zinline-mir=no"

rustc +baseline $RUSTFLAGS repro.rs -o baseline.s
IGNORE_INLINE_COST=1 rustc +force-panic-abort $RUSTFLAGS repro.rs -o abort.s

rustc +master -O --crate-type=rlib --emit=asm -Zinline-mir=no repro.rs -o master.s
IGNORE_INLINE_COST=1 rustc +master -O --crate-type=rlib --emit=asm repro.rs -o master2.s
rustc +master -O --crate-type=rlib --emit=asm -Zinline-mir=no -Cpanic=abort repro.rs -o master-abort.s
IGNORE_INLINE_COST=1 rustc +master -O --crate-type=rlib --emit=asm -Cpanic=abort repro.rs -o master-abort2.s
