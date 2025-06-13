#!/bin/sh

# This is very ugly...
# Basically we want to link against Rust's LLVM but
# it's linked with `-Wl,-Bsymbolic` flag (too speed up runtime?).
# 
# This introduces a known (https://github.com/llvm/llvm-project/issues/50762)
# subtle bug: IDs of passes in library do not match IDs of passes in client
# which causes runtime assertions when LLVM fails to find them via `AM::getResult`-like APIs.
# 
# We work around this via intermediate dummy library (same way as rustc with rustc_driver library).

set -eu
set -x

rm -f libCountLoops.so CountLoops

CXX=g++
CFG=$HOME/src/rust/baseline/build/x86_64-unknown-linux-gnu/ci-llvm/bin/llvm-config

CXXFLAGS='-g -O2'

LDFLAGS=" $($CFG --ldflags)"
LIBS="$($CFG --libs)"

$CXX $CXXFLAGS -fPIC -shared $($CFG --cxxflags --ldflags) -Wl,-rpath=$($CFG --libdir) CountLoops.cpp $($CFG --libs) -o libCountLoops.so
$CXX $CXXFLAGS -x c++ /dev/null -Wl,-rpath=$PWD -L. -lCountLoops -o CountLoops
