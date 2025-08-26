#!/bin/sh

# See comments in bounds/count-loops/build.sh

set -eu
set -x

rm -f libCount.so Count

CXX=g++
CFG=$HOME/src/rust/no-overflow-checks/build/x86_64-unknown-linux-gnu/ci-llvm/bin/llvm-config

CXXFLAGS='-g -O2'

LDFLAGS=" $($CFG --ldflags)"
LIBS="$($CFG --libs)"

$CXX $CXXFLAGS -fPIC -shared $($CFG --cxxflags --ldflags) -Wl,-rpath=$($CFG --libdir) Count.cpp $($CFG --libs) -o libCount.so
$CXX $CXXFLAGS -x c++ /dev/null -Wl,-rpath=$PWD -L. -lCount -o Count
