#!/bin/bash

# Script to run interesting tests from Phoronix Test Suite.
#
# All weird parts are due to issues with environment which I intend to
# run them on.

set -eu
#set -x

if ! test -t 1 -o -n "${__SED_ENABLED:-}"; then
  # PTS prints colors to logfiles, fix this
  __SED_ENABLED=1 "$0" "$@" | sed 's/\x1b\[[0-9;]*m//g'
  exit $?
fi

# Artifacts of my PHP setup...
PREFIX=$HOME/src/php-tree/root
. $PREFIX/env
export PHP_INI_SCAN_DIR=$PREFIX/etc/php/8.2/cli/conf.d
PHP="php -c $PREFIX/etc/php/8.2/cli"

PTS_DIR=$HOME/src/phoronix-test-suite
PTS_LOCAL_DIR=$HOME/.phoronix-test-suite

# A list of relevant tests:
#   - come from popular projects
#   - no external dependencies (I don't have root access on server)
#   - don't take too much time (e.g. ffmpeg, fftw, redis were removed)
#   - produce stable results (e.g. all compress/XXX were removed)
#   - respect CFLAGS/CXXFLAGS
#     (e.g. mkl-dnn, onednn, etc. reset them and nginx uses CFLAGS for both)
#   - total runtime of tests under 6 hours
#     (that's free time on server that I have)
tt='pts/apache pts/botan pts/bullet pts/coremark pts/crafty pts/c-ray pts/gcrypt pts/gmpbench pts/luajit pts/nginx pts/openssl pts/polybench-c pts/povray pts/simdjson pts/z3'

export NO_EXTERNAL_DEPENDENCIES=TRUE

for t in $tt; do
  $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-install $t
  setarch -R $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-benchmark $t
  rm -rf $PTS_LOCAL_DIR/installed-tests/$t*
done
