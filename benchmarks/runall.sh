#!/bin/sh

# Simple wrapper for runner.py
# which clones everything, builds and runs benchmarks
#
# Run like
#   $ RUNNER_ARGS="-j6 -r '' -o meilisearch,oxipng,rav1e,ruff,tokio" ./runall.sh

set -eu

D=$(dirname $0)

WORKDIR=$PWD/repos
if test -d $WORKDIR; then
  echo >&2 "Directory $WORKDIR exists, please remove it"
  exit 1
fi
mkdir $WORKDIR

for t in baseline bounds; do
  eval "$D/runner.py -p $WORKDIR -t $t --clean --clone ${RUNNER_ARGS:-}" 2>&1 | tee $t.log
done

# TODO: compare geomeans
