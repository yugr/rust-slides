#!/bin/sh

set -eu
#set -x

bench() {
  for _ in $(seq 5); do
    setarch -R "$@"
  done
}

CXXFLAGS='-O2 -DNDEBUG -Wall -Wextra -Werror'

# GCC
# TODO: use recent release

g++ $CXXFLAGS test.cc

echo "GCC (libstdc++)"
bench ./a.out

# Clang

CLANG_PREFIX=$HOME/src/llvm-project/install

echo "Clang (libc++)"

$CLANG_PREFIX/bin/clang++ \
  $CXXFLAGS \
  -stdlib=libc++ \
  -nostdinc++ -isystem $CLANG_PREFIX/include/c++/v1 -isystem $CLANG_PREFIX/include/x86_64-unknown-linux-gnu/c++/v1 \
  -L $CLANG_PREFIX/lib/x86_64-unknown-linux-gnu -lc++abi -lunwind -Wl,-rpath,$CLANG_PREFIX/lib/x86_64-unknown-linux-gnu \
  test.cc

bench ./a.out
