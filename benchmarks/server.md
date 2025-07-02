This file contains instructions for setting up server for benchmarking.

# BIOS settings

Disable frequency scaling, hyperthreading, HW prefetching, Turbo Boost, Intel Speed Shift, etc. in BIOS settings.

# Run in non-GUI mode

To boot to non-GUI mode on systemd systems see https://linuxconfig.org/how-to-disable-enable-gui-in-ubuntu-22-04-jammy-jellyfish-linux-desktop
(`sudo init 1` otherwise).

# Disable networking (TOO INCONVENIENT)

Disable network via
```
# Ubuntu (note that this is a permanent setting)
$ nmcli networking off

# Other suggestions, didn't work for me
$ sudo /etc/init.d/networking stop
$ systemctl stop networking.service
```

Note that projects may not be buildable after that because dependencies won't download
(so need to build without `--clone` and with `--no-clean`).

TODO: check if this is important for stability

# Reserve cores for benchmarking (NOT APPLICABLE)

Add to `/etc/default/grub`:
```
GRUB_CMDLINE_LINUX_DEFAULT="nohz=on nohz_full=8-15 kthread_cpus=0-7 irqaffinity=0-7 isolcpus=domain,managed_irq,8-15"
```
(this assumes that cores 0-7 are left to system and 8-15 are reserved for benchmarks).
The run
```
$ sudo update-grub
```
and reboot.

Also add permissions to change scheduling policy for ordinary users:
```
$ sudo setcap cap_sys_nice=ep /usr/bin/chrt
```
(otherwise kernel [will schedule all threads which run under `taskset` on same core](https://serverfault.com/questions/573025/taskset-not-working-over-a-range-of-cores-in-isolcpus)).

You can now use `chrt -f 1 taskset 0xff00 ...` to run benchmarks on reserved cores.

UNFORTUNATELY CORE RESERVATION IS NOT APPLICABLE TO RUST BENCHMARKS:
  - most benchmarks rely on `std::thread::available_parallelism` which ignores affinity mask
  - so they start more worker threads than available cores
  - this causes noise levels to skyrocket (10x, reproduced on Ubuntu 22 kernel 6.8.0-60-generic)
  - for some benchmarks this maybe can be controlled by `TOKIO_WORKER_THREADS` or `RAYON_NUM_THREADS`
    but core `available_parallelism` can not be controlled by environment variable

# Fix frequency

Set scaling governor to `performance` via
```
# Give CPU startup routines time to settle
$ sleep 120
$ echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

# Increase priority

Add to `/etc/security/limits.conf`:
```
USERNAME soft nice -20
USERNAME hard nice -20
```
and run benchmarks under `nice -n -20 ...`.

# Disable ASLR

Run benchmarks under `setarch -R ...`.

# Future work

The noise is still high (2-4%) so these things should be tried:
  - single-user mode
  - reduce thread count (maybe even to single core):
    * control `std::thread::available_parallelism` via env. variable (need to patch stdlib)
      + bevy, ruff (also `TY_MAX_PARALLELISM` env. variable), uv, rust
    * reduce parallelism in Rayon via `RAYON_NUM_THREADS` env. variable:
      + meilisearch, oxipng, rav1e, SpacetimeDB, ruff
    * reduce parallelism in Tokio via `TOKIO_WORKER_THREADS` env. variable:
      + tokio
    * no parallelism:
      + nalgebra, regex
    * what about zed ?
