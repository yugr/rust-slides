#!/bin/sh

set -eu
set -x

FFMPEG=$HOME/src/ffmpeg-8.0.1
X264=$HOME/src/x264  # https://code.videolan.org/videolan/x264 0480cb05
FLV=big_buck_bunny_360p_1mb.flv  # https://zatoichi-engineer.github.io/2017/10/04/stack-smashing-protection.html#performance-cost

B=$PWD/build
J=$((($(nproc) + 1)/ 2))
OUT=$PWD/results
REPEAT=10
V=0
NO_RUN=
ORIGIN=$(readlink -f $(dirname $0))

if ! test -f $FLV; then
  wget https://zatoichi-engineer.github.io/assets/data/$FLV
fi

usage() {
  cat <<EOF
Usage: $(basename $0) [OPT]... OPTS.CFG
Run LLVM tests.

Options:
  --ffmpeg path   Path to ffmpeg (default $FFMPEG).
  --x264 path     Path to x264 (default $X264).
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
Usage: $(basename $0) [OPT]... OPTS.CFG
Run \`$(basename $0) -h' for more details.
EOF
  exit 1
}

me=$(basename $0)

ARGS=$(getopt -o 'hj:n:o:v' --long 'ffmpeg:,x264:,no-run,verbose,help' -n "$(basename $0)" -- "$@")
eval set -- "$ARGS"

while true; do
  case "$1" in
    --ffmpeg)
      FFMPEG="$2"
      shift 2
      ;;
    --x264)
      X264="$2"
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

test $# -eq 1 || usage_short

OPTS_CONFIG="$1"

sanitize() {
  echo "$1" | sed -e 's/#.*//; s/^ *//; s/ *$//'
}

mkdir -p $OUT

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')

  rm -f $OUT/$name.log
done < "$OPTS_CONFIG"

if ! test -d $FFMPEG/libavcodec; then
  echo >&2 "'$FFMPEG' is not an ffmpeg directory"
  exit 1
fi
FFMPEG=$(readlink -f $FFMPEG)

if ! test -f $X264/x264.h; then
  echo >&2 "'$X264' is not a libx264 directory"
  exit 1
fi
X264=$(readlink -f $X264)

tmp=$(mktemp)

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  name=$(echo "$cfg" | awk -F: '{print $1}')
  cc=$(echo "$cfg" | awk -F: '{print $2}')
  cflags=$(echo "$cfg" | awk -F: '{print $3}')
  ldflags=$(echo "$cfg" | awk -F: '{print $4}')
  libs=$(echo "$cfg" | awk -F: '{print $5}')

  prefix=$(dirname $(which $cc))/..

  cflags=$(echo "$cflags" | sed -e "s!ORIGIN!$ORIGIN!g; s!PREFIX!$prefix!g")
  cxxflags=$(echo "$cflags" | sed -e "s!ORIGIN!$ORIGIN!g; s!PREFIX!$prefix!g")
  ldflags=$(echo "$ldflags" | sed -e "s!ORIGIN!$ORIGIN!g; s!PREFIX!$prefix!g")

  baseflags='-O2 -DNDEBUG'

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

  echo "Building config $name..."

  rm -rf "$B"

  (
    mkdir -p "$B"/x264-build
    cd "$B"/x264-build
    CC=$cc $X264/configure --prefix="$B"/x264-install --extra-cflags="$baseflags $cflags" --extra-ldflags="$ldflags" --enable-shared --enable-static
    make -j$J V=1
    make -j$J install
  )

  (
    mkdir -p "$B"/ffmpeg-build
    cd "$B"/ffmpeg-build
    export PKG_CONFIG_PATH=$B/x264-install/lib/pkgconfig
    $FFMPEG/configure --prefix=$B/ffmpeg-install --cc=$cc --cxx=$cxx --extra-cflags="$baseflags $cflags" --extra-cxxflags="$baseflags $cflags" --extra-ldflags="$baseflags $ldflags -Wl,-rpath,$B/x264-install/lib" --enable-libx264 --enable-gpl
    make -j$J V=1
    make -j$J install
  )

  test -z "$NO_RUN" || continue

  echo "Benchmarking $name..."
  for i in $(seq $REPEAT); do
     # TODO: more testcases ?
    /usr/bin/time -o $tmp setarch -R $B/ffmpeg-install/bin/ffmpeg -y -i $FLV -c:v libx264 -c:a aac -threads 1 out.mp4 < /dev/null > /dev/null 2>&1
    cat $tmp >> $OUT/$name.log
  done
done < "$OPTS_CONFIG"

rm -f $tmp
