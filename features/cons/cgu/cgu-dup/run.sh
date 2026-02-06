#!/bin/sh

set -eu
set -x

rm -rf rmeta* *.bc *.o *.ll
rustc +baseline -Copt-level=0 -Ccodegen-units=4 main.rs -Csave-temps
~/src/rust/rust/build/x86_64-unknown-linux-gnu/llvm/bin/llvm-dis *.no-opt.bc
grep foo *.ll

rm -rf rmeta* *.bc *.o *.ll
rustc +baseline -Copt-level=0 -Ccodegen-units=4 main.rs -Csave-temps --cfg generic
~/src/rust/rust/build/x86_64-unknown-linux-gnu/llvm/bin/llvm-dis *.no-opt.bc
grep foo *.ll
