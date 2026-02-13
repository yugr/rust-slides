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
CONFIG=$(dirname $0)/config.txt

export NO_EXTERNAL_DEPENDENCIES=TRUE

sanitize() {
  echo "$cfg" | sed -e 's/#.*//; s/^ *//; s/ *$//'
}

while read cfg; do
  cfg=$(sanitize "$cfg")
  test -n "$cfg" || continue

  cflags=$(echo "$cfg" | awk -F: '{print $1}')
  cxxflags=$(echo "$cfg" | awk -F: '{print $2}')
  tt=$(echo "$cfg" | awk -F: '{print $3}')

  for t in $tt; do
    (
      # Keep default Autoconf flags
      export CFLAGS="${CFLAGS:--g -O2} $cflags"
      export CXXFLAGS="${CXXFLAGS:--g -O2} $cxxflags"
      export LDFLAGS="$CFLAGS"
      $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-install $t
      setarch -R $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-benchmark $t
    )
    rm -rf $PTS_LOCAL_DIR/installed-tests/$t*
  done
done < "$CONFIG"
