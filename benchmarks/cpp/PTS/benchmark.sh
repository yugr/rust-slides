#!/bin/bash

# TODO:
# - reduce stdev
# - limit repeats for long tests (e.g. 10 min. ?)
# - log comparator

set -eu
set -x

# Artifacts of my PHP setup...
PREFIX=$HOME/src/php-tree/root
. $PREFIX/env
export PHP_INI_SCAN_DIR=$PREFIX/etc/php/8.2/cli/conf.d
PHP="php -c $PREFIX/etc/php/8.2/cli"

PTS_DIR=$HOME/src/phoronix-test-suite
PTS_LOCAL_DIR=$HOME/.phoronix-test-suite

# A list of relevant tests:
#   - popular projects
#   - no external dependencies (I don't have root access on server)
#   - don't take too much time (e.g. ffmpeg, fftw, redis were removed)
#   - produce stable results (e.g. all compress/XXX were removed)
tt='pts/apache pts/c-ray pts/openssl pts/botan pts/bullet pts/coremark pts/gmpbench pts/nginx pts/luajit pts/polybench-c pts/povray pts/simdjson'

export NO_EXTERNAL_DEPENDENCIES=TRUE

for t in $tt; do
  $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-install $t
  $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-benchmark $t
  rm -rf $PTS_LOCAL_DIR/installed-tests/$t*
done
