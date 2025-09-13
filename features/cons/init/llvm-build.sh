#!/bin/sh

set -eu
set -x

# llvmorg-20.1.7
LLVM=$HOME/src/llvm-project
J=$(($(nproc) / 2))
REPEAT=3

tmp=$(mktemp)

build() {
  local B="$1"
  local CC="$2"
  local CXX="$3"
  local CXXFLAGS="$4"

  rm -rf $B
  cmake -G Ninja \
    -DCMAKE_C_COMPILER=$CC -DCMAKE_CXX_COMPILER=$CXX -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-O2 $CXXFLAGS" -DLLVM_ENABLE_ASSERTIONS=OFF \
    -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF \
    -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang \
    -B "$B" "$LLVM"/llvm
  cmake --build "$B" -- -j$J clang
}

bench() {
  local B="$1"
  local F="$2"

  echo "=== $B: $F"

  for i in $(seq 1 $REPEAT); do
    /usr/bin/time -o $tmp setarch -R $B/bin/clang -O2 -w -S -o /dev/null $F 2>/dev/null
    cat $tmp
  done
}

build build-bootstrap gcc g++ ''

CC=$PWD/build-bootstrap/bin/clang
CXX=$PWD/build-bootstrap/bin/clang++

# Add -save-temps to generate .bc files for analysis
build build-ref $CC $CXX ''
build build-new $CC $CXX '-ftrivial-auto-var-init=zero'

for B in build-ref build-new; do
  for f in $(dirname $0)/files/*.ii; do
    bench $B $f
  done
done

rm -f $tmp
