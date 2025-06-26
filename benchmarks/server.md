This file contains instructions for setting up server for benchmarking.

# BIOS settings

Disable frequency scaling, hyperthreading, HW prefetching, Turbo Boost, Intel Speed Shift, etc. in BIOS settings.

# Run in non-GUI mode

To boot to non-GUI mode on systemd systems see https://linuxconfig.org/how-to-disable-enable-gui-in-ubuntu-22-04-jammy-jellyfish-linux-desktop
(`sudo init 1` otherwise).

# Disable networking

Disable network via
```
# Ubuntu (note that this is a permanent setting)
$ nmcli networking off

# Other suggestions, didn't work for me
$ sudo /etc/init.d/networking stop
$ systemctl stop networking.service
```

Note that projects may not be buildable after that because dependencies won't download.

TODO: check if this is important for stability

# Reserve cores for benchmarking

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

You can now use `chrt -r 1 taskset 0xff00 ...` to run benchmarks on reserved cores.

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
