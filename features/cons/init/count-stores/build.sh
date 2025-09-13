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

rm -f libCount.so Count

CXX=g++
CFG=$HOME/tasks/llvm-bench-rust/build-bootstrap/bin/llvm-config

CXXFLAGS='-g -O2'

LDFLAGS=" $($CFG --ldflags)"
LIBS="$($CFG --libs)"

$CXX $CXXFLAGS -fPIC -shared $($CFG --cxxflags --ldflags) -Wl,-rpath=$($CFG --libdir) Count.cpp $($CFG --libs) -o libCount.so
$CXX $CXXFLAGS -x c++ /dev/null -Wl,-rpath=$PWD -L. -lCount -lz -lzstd -o Count
