#!/bin/sh

set -eu
set -x

LLVM=$HOME/src/rust/baseline/build/x86_64-unknown-linux-gnu/ci-llvm

CXX=g++

CXXFLAGS='-std=c++17 -fno-rtti -fno-exceptions'
CXXFLAGS="$CXXFLAGS -I$LLVM/include"
CXXFLAGS="$CXXFLAGS -Wall -Werror"
CXXFLAGS="$CXXFLAGS -g -O0"

LDFLAGS="-Wl,-rpath=$LLVM/lib"
LIBS="$LLVM/lib/libLLVM-20-rust-1.87.0-nightly.so"

$CXX $CXXFLAGS $LDFLAGS CountLoops.cpp $LIBS -o CountLoops
