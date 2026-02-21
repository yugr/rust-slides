#!/bin/sh

set -eu
set -x

# llvmorg-20.1.7
LLVM=.
B=./build
J=$((($(nproc) + 1)/ 2))
OUT=./results
REPEAT=10
V=0
NO_RUN=
ORIGIN=$(readlink -f $(dirname $0))

usage() {
  cat <<EOF
Usage: $(basename $0) [OPT]... OPTS.CFG TESTS.CFG
Run LLVM tests.

Options:
  --llvm path     Path to LLVM (default $LLVM).
  -j N            Build parallelism (default $J).
  -o OUTDIR       Where to store results (default $OUT).
  -n REPEAT       How many times to compile each file (default $REPEAT).
  --no-run        Just build, do not run benchmarks.
  --help, -h      Print help and exit.
  --verbose, -v   Print diagnostic info
                  (can be specified more than once).

Examples:
  \$ $(basename $0) configs.txt
EOF
  exit
}

usage_short() {
  cat >&2 <<EOF
Usage: $(basename $0) [OPT]... OPTS.CFG TESTS.CFG
Run \`$(basename $0) -h' for more details.
EOF
  exit 1
}

me=$(basename $0)

ARGS=$(getopt -o 'hj:n:o:v' --long 'llvm:,no-run,verbose,help' -n "$(basename $0)" -- "$@")
eval set -- "$ARGS"

while true; do
  case "$1" in
    --llvm)
      LLVM="$2"
      shift 2
      ;;
    -j)
      J=$2
      shift 2
      ;;
    -o)
      OUT=$2
      shift 2
      ;;
    -n)
      REPEAT=$2
      shift 2
      ;;
    --no-run)
      NO_RUN=1
      shift
      ;;
    -h | --help)
      usage
      ;;
    -v | --verbose)
      V=$((V + 1))
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      error "unknown option: $1"
      ;;
    *)
      error 'internal error'
      ;;
  esac
done

test $# -eq 2 || usage_short

OPTS_CONFIG="$1"
TESTS_CONFIG="$2"

sanitize() {
  echo "$1" | sed -e 's/#.*//; s/^ *//; s/ *$//'
}

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')

  mkdir -p $OUT/$name
  rm -f $OUT/$name/*.log
done < "$OPTS_CONFIG"

if ! test -f $LLVM/llvm/CMakeLists.txt; then
  echo >&2 "'$LLVM' is not an LLVM directory"
  exit 1
fi

tmp=$(mktemp)

regenerate_tests() {
  cmake -G Ninja \
    -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS='-save-temps' \
    -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang \
    -B "$B" "$LLVM"/llvm

  files=
  objs=
  while read cfg; do
    cfg=$(sanitize "$cfg")
    test -n "$cfg" || continue

    name=$(echo "$cfg" | awk -F: '{print $1}')
    obj=$(echo "$cfg" | awk -F: '{print $2}')

    files="$files $B/$name"
    objs="$files $obj"
  done < "$TESTS_CONFIG"

  cmake --build "$B" -- -j$J $objs

  mv $files .
}

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')
  if ! test -f $name; then
    regenerate_tests
    break
  fi
done < "$TESTS_CONFIG"

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')
  cc=$(echo "$cfg" | awk -F: '{print $2}')
  cxxflags=$(echo "$cfg" | awk -F: '{print $3}')
  ldflags=$(echo "$cfg" | awk -F: '{print $4}')
  llvmflags=$(echo "$cfg" | awk -F: '{print $5}')

  prefix=$(dirname $(which $cc))/..

  cxxflags=$(echo "$cxxflags" | sed -e "s!ORIGIN!$ORIGIN!g; s!PREFIX!$prefix!g")
  ldflags=$(echo "$ldflags" | sed -e "s!ORIGIN!$ORIGIN!g; s!PREFIX!$prefix!g")
  llvmflags=$(echo "$llvmflags" | sed -e "s!ORIGIN!$ORIGIN!; s!PREFIX!$prefix!g")

  case $cc in
    gcc)
      cxx=g++
      ;;
    clang)
      cxx=clang++
      ;;
    *)
      echo "Unknown compiler: $cc"
      exit 1
  esac

  if test -z "$name"; then
    echo "Failed to parse config: $cfg"
    exit 1
  fi

  echo "Building $name..."

  rm -rf "$B"

  # 1) We need to set CMAKE_C_COMPILER even though we don't use it
  #   because Cmake needs it for config tests...
  # 2) No need to pass "-O2 -DNDEBUG" because they will be overridden
  #   by default CMAKE_CXX_FLAGS_RELEASE (-O3 -DNDEBUG)
  cmake -G Ninja \
    -DCMAKE_C_COMPILER=$cc -DCMAKE_CXX_COMPILER=$cxx -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="$cxxflags" -DCMAKE_EXE_LINKER_FLAGS="$ldflags" \
    $llvmflags \
    -DLLVM_ENABLE_WARNINGS=OFF -DLLVM_ENABLE_LLD=ON -DLLVM_PARALLEL_LINK_JOBS=1 -DLLVM_APPEND_VC_REV=OFF \
    -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS=clang \
    -B "$B" "$LLVM"/llvm
  cmake --build "$B" -- -j$J clang

  test -z "$NO_RUN" || continue

  echo "Benchmarking $name..."
  while read t; do
    t=$(sanitize "$t")
    test -n "$t" || continue

    file=$(echo "$t" | awk -F: '{print $1}')

    for i in $(seq 1 $REPEAT); do
      /usr/bin/time -ao $OUT/$name/$(basename $file).log setarch -R $B/bin/clang -O2 -w -S -o /dev/null $file
    done
  done < "$TESTS_CONFIG"
done < "$OPTS_CONFIG"

rm -f $tmp
