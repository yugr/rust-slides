#!/bin/sh

set -eu
set -x

#RUSTFLAGS=-O
RUSTFLAGS='-Zunsound-mir-opts -Zmir-opt-level=4 -Zmir-enable-passes=+DestinationPropagation,+RenameReturnPlace'

rustc $RUSTFLAGS --emit asm --crate-type=lib repro.rs -o- | c++filt
