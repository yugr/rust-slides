#!/bin/sh

set -eu
set -x

rustc -O --emit asm --crate-type=lib repro.rs -o- | c++filt
