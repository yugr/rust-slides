#!/bin/bash

# Script to run interesting tests from Phoronix Test Suite.
# Uses https://github.com/yugr/cc-wrappers

set -eu
#set -x

PTS_DIR=$HOME/src/phoronix-test-suite
PTS_LOCAL_DIR=$HOME/.phoronix-test-suite
PHP=${PHP:-php}

OPTS_CONFIG=$(dirname $0)/opts.txt
TESTS_CONFIG=$(dirname $0)/tests.txt

TIME=time
#TIME=

#export NO_EXTERNAL_DEPENDENCIES=TRUE

# Some files in gcrypt need to be compiled w/ -O0
export WRAPPER_BLACKLIST='jitterentropy.c\|rndjent.c'

sanitize() {
  echo "$1" | sed -e 's/#.*//; s/^ *//; s/ *$//'
}

if ! which gcc | grep -q 'cc-wrappers'; then
  echo >&2 'You need to add cc-wrappers to PATH'
  exit 1
fi

if test -z "${WRAPPER_CC:-}" -o -z "${WRAPPER_CXX:-}"; then
  echo >&2 'You need to define WRAPPER_CC and WRAPPER_CXX environment variables'
  exit 1
fi

baseflags="-O2 -DNDEBUG -fpermissive -w -Wno-error"

# Disable protections which are often enabled by default (e.g. on Ubuntu)
# but perhaps it's irrelevant for Clang ?
baseflags="$baseflags -fno-stack-protector -fno-stack-clash-protection -U_FORTIFY_SOURCE"

prefix=$(dirname $(readlink -f $WRAPPER_CC))/..

while read opts; do
  opts=$(sanitize "$opts")
  test -n "$opts" || continue

  name=$(echo "$opts" | awk -F: '{print $1}')
  rm -f $name.log
done < "$OPTS_CONFIG"

while read opts; do
  opts=$(sanitize "$opts")
  test -n "$opts" || continue

  name=$(echo "$opts" | awk -F: '{print $1}')
  optflags=$(echo "$opts" | awk -F: '{print $2}' | sed -e "s!PREFIX!$prefix!g")

  echo "Testing $name..."

  while read tests; do
    tests=$(sanitize "$tests")
    test -n "$tests" || continue

    cflags=$(echo "$tests" | awk -F: '{print $1}' | sed -e "s!PREFIX!$prefix!g")
    cxxflags=$(echo "$tests" | awk -F: '{print $2}' | sed -e "s!PREFIX!$prefix!g")
    tt=$(echo "$tests" | awk -F: '{print $3}')

    for t in $tt; do
      echo "Running $t..."
      rm -rf $PTS_LOCAL_DIR/installed-tests/$t*
      (
        export WRAPPER_CFLAGS="$baseflags $optflags $cflags"
        export WRAPPER_CXXFLAGS="$baseflags $optflags $cxxflags"
        $TIME $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-install $t
        $TIME setarch -R $PHP $PTS_DIR/pts-core/phoronix-test-suite.php batch-benchmark $t
      ) |& sed 's/\x1b\[[0-9;]*m//g' >> $name.log  # PTS prints colors to logfiles, fix this
    done
  done < "$TESTS_CONFIG"
done < "$OPTS_CONFIG"
