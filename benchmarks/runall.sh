#!/bin/bash

# Simple driver for Python scripts: clones everything, builds and
# runs benchmarks and compares results.
#
# Run `runall.sh --help` for details.

set -eu
set -o pipefail

me=$(basename $0)

V=0
BASELINE=baseline

error() {
  printf "$(basename $0): error: $@\\n" >&2
  exit 1
}

warn() {
  printf "$(basename $0): warning: $@\\n" >&2
}

usage() {
  cat <<EOF
Usage: $(basename $0) [OPT]... TOOLCHAIN...
Builds and runs benchmarks under multiple toolchains.

Options:
  --help, -h                     Print help and exit.
  --baseline TC                  Compare all results against TC (default '$BASELINE').
  --clone                        Re-create repos.
  -r ARGS, --runner-args=ARGS    Additional arguments for runner.py.
  --verbose, -v                  Print diagnostic info
                                 (can be specified more than once).

Examples:
  # Run benchmarks without fancy dependencies with sensible flags
  \$ $(basename $0) --runner-args "-r 'chrt -r 1 taskset 0xf0 nice -n -20 setarch -R' --only SpacetimeDB,bevy,meilisearch,nalgebra,oxipng,rav1e,regex,ruff,rust_serialization_benchmark,tokio" baseline
EOF
  exit
}

usage_short() {
  cat >&2 <<EOF
Usage: $(basename $0) [OPT]... TOOLCHAIN...
Run \`$(basename $0) -h' for more details.
EOF
  exit 1
}

CLONE=
RUNNER_ARGS=

ARGS=$(getopt -o 'hr:v' --long 'help,baseline:,clone,runner-args:,verbose' -n "$(basename $0)" -- "$@")
eval set -- "$ARGS"

while true; do
  case "$1" in
    -h | --help)
      usage
      ;;
    --baseline)
      BASELINE="$2"
      shift 2
      ;;
    --clone)
      CLONE=--clone
      shift
      ;;
    -r | --runner-args)
      RUNNER_ARGS="$2"
      shift 2
      ;;
    -v | --verbose)
      V=$((V + 1))
      shift
      ;;
    --)
      shift
      TOOLCHAINS="$@"
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

if test -z "$TOOLCHAINS"; then
  echo >&2 "No toolchains specified, exiting"
  exit 1
fi

D=$(dirname $0)

mkdir -p results
for t in $TOOLCHAINS; do
  rm -rf results/$t
done

WORKDIR=$PWD/repos
if test -n "$CLONE"; then
  rm -rf $WORKDIR
  mkdir $WORKDIR
fi

for t in $TOOLCHAINS; do
  mkdir -p results/$t
  eval "$D/runner.py -p $WORKDIR -t $t $CLONE $RUNNER_ARGS" 2>&1 | tee results/$t/runner.log
  mv $WORKDIR/*.json results/$t
done

for t in $TOOLCHAINS; do
  if test $t = $BASELINE; then
    continue
  fi
  echo "### Comparing $t against $BASELINE:"
  $D/compare.py results/$BASELINE results/$t
done
