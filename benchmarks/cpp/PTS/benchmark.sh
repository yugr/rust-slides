#!/bin/bash

set -eu
set -x

# Artifacts of my PHP setup...
PREFIX=$HOME/src/php-tree/root
. $PREFIX/env
export PHP_INI_SCAN_DIR=$PREFIX/etc/php/8.2/cli/conf.d
PHP='php -c $PREFIX/etc/php/8.2/cli'

# A list of relevant tests (popular projects, no external dependencies)
tt='pts/apache pts/botan pts/bullet pts/c-ray pts/compress-gzip pts/compress-lz4 pts/compress-pbzip2 pts/compress-rar pts/compress-xz pts/compress-zstd pts/coremark pts/ffmpeg pts/fftw pts/gmpbench pts/luajit pts/lzbench pts/nginx pts/openjpeg pts/openssl pts/polybench-c pts/povray pts/redis pts/simdjson pts/z3 git/clickhouse'

export NO_EXTERNAL_DEPENDENCIES=TRUE

for t in $tt; do
  $PHP pts-core/phoronix-test-suite.php batch-install $t
  $PHP pts-core/phoronix-test-suite.php batch-benchmark $t
done
