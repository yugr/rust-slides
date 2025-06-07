#!/bin/sh

set -eu
set -x

CXX=g++

CXXFLAGS='-std=c++17 -fno-rtti -fno-exceptions'
CXXFLAGS="$CXXFLAGS -Wall -Werror"
CXXFLAGS="$CXXFLAGS -g -O0"

LLVM=$HOME/src/rust/baseline/build/x86_64-unknown-linux-gnu/ci-llvm

$CXX $CXXFLAGS main.cpp -I$LLVM/include -Wl,-rpath=$LLVM/lib $LLVM/lib/libLLVM.so.20.1-rust-1.87.0-nightly
