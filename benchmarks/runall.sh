#!/bin/bash

# Simple wrapper for runner.py
# which clones everything, builds and runs benchmarks
#
# Run like
#   $ RUNNER_ARGS="-j6 -r '' -o meilisearch,oxipng,rav1e,ruff,tokio" ./runall.sh

set -eu
set -o pipefail

me=$(basename $0)

TOOLCHAINS='baseline bounds'
V=0

usage() {
  cat <<EOF
Usage: $(basename $0) [OPT]...
Describe script here.

Options:
  --help, -h                     Print help and exit.
  --no-clean                     Do not clean before building (for debug).
  --reclone                      Re-create repos.
  -r ARGS, --runner-args=ARGS    Additional arguments for runner.py.
  -t TS, --toolchains TS         Toolchains to test (default $TOOLCHAINS).
  --verbose, -v                  Print diagnostic info
                                 (can be specified more than once).

Examples:
  \$ $(basename $0) --runner-args "-j6 -r '' --clean -o SpacetimeDB,bevy,meilisearch,oxipng,rav1e,ruff,tokio"
EOF
  exit
}

usage_short() {
  cat >&2 <<EOF
Usage: $(basename $0) [OPT]... ARG
Run \`$(basename $0) -h' for more details.
EOF
  exit 1
}

RECLONE=
CLEAN=--clean
RUNNER_ARGS=

ARGS=$(getopt -o 'hr:t:v' --long 'help,no-clean,reclone,runner-args:,toolchains:,verbose' -n "$(basename $0)" -- "$@")
eval set -- "$ARGS"

while true; do
  case "$1" in
    -h | --help)
      usage
      ;;
    --no-clean)
      CLEAN=
      shift
      ;;
    --reclone)
      RECLONE=1
      shift
      ;;
    -r | --runner-args)
      RUNNER_ARGS="$2"
      shift 2
      ;;
    -t | --toolchains)
      TOOLCHAINS="$2"
      shift 2
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

D=$(dirname $0)

mkdir -p results
for t in $TOOLCHAINS; do
  rm -rf results/$t
done

WORKDIR=$PWD/repos
if test -n "$RECLONE"; then
  rm -rf $WORKDIR
  mkdir $WORKDIR
elif test -d $WORKDIR; then
  echo >&2 "Directory $WORKDIR already exists"
  exit 1
fi

for t in $TOOLCHAINS; do
  mkdir -p results/$t
  eval "$D/runner.py -p $WORKDIR -t $t --clone $CLEAN $RUNNER_ARGS" 2>&1 | tee results/$t/runner.log
  mv $WORKDIR/*.json results/$t
done

# TODO: compare geomeans
