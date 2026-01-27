#!/bin/sh

set -eu
set -x

echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Fix frequency at 1.5 GHz
echo 1500000 | sudo tee /sys/devices/system/cpu/*/cpufreq/scaling_min_freq /sys/devices/system/cpu/*/cpufreq/scaling_max_freq
