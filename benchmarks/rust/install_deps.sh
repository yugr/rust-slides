#!/bin/sh

# Install benchmark dependencies

set -eu
set -x

sudo apt update

# Bevy (from https://github.com/bevyengine/bevy/blob/latest/docs/linux_dependencies.md)
sudo apt-get install -y g++ pkg-config libx11-dev libasound2-dev libudev-dev libxkbcommon-x11-0

# rav1e
sudo apt install -y nasm
cargo install cargo-criterion

# veloren
sudo apt install -y libxkbcommon-x11-dev

# zed (from zed/script/linux)
sudo apt install -y gcc g++ libasound2-dev libfontconfig-dev libwayland-dev libx11-xcb-dev libxkbcommon-x11-dev libssl-dev libzstd-dev libvulkan1 libgit2-dev make cmake clang jq git curl gettext-base elfutils libsqlite3-dev musl-tools musl-dev build-essential

# Do not generate Criterion reports (optional)
sudo apt uninstall -y gnuplot

# For uv
sudo apt install -y python3-venv
