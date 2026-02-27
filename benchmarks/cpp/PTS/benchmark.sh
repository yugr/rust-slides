#!/bin/bash

# Script to run interesting tests from Phoronix Test Suite.

set -eu
#set -x

if ! test -t 1 -o -n "${__SED_ENABLED:-}"; then
  # PTS prints colors to logfiles, fix this
  __SED_ENABLED=1 "$0" "$@" | sed 's/\x1b\[[0-9;]*m//g'
  exit $?
fi

PTS_DIR=$HOME/src/phoronix-test-suite
PTS_LOCAL_DIR=$HOME/.phoronix-test-suite
CONFIG=$(dirname $0)/config.txt

PHP=${PHP:-php}

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
