#!/bin/sh

# Install benchmark dependencies

set -eu
set -x

# Bevy (from https://github.com/bevyengine/bevy/blob/latest/docs/linux_dependencies.md)
sudo apt-get install g++ pkg-config libx12-dev libasound2-dev libudev-dev libxkbcommon-x11-0

# rav1e
sudo apt install nasm
cargo install cargo-criterion

# veloren
sudo apt install libxkbcommon-x11-dev

# zed (from zed/script/linux)
sudo apt install gcc g++ libasound2-dev libfontconfig-dev libwayland-dev libx11-xcb-dev libxkbcommon-x11-dev libssl-dev libzstd-dev libvulkan1 libgit2-dev make cmake clang jq git curl gettext-base elfutils libsqlite3-dev musl-tools musl-dev build-essential

# For criterion (optional)
sudo apt install gnuplot
