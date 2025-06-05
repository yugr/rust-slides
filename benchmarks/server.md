This file contains instructions for setting up server for benchmarking.

# Reserve cores for benchmarking

Add to `/etc/default/grub`:
```
GRUB_CMDLINE_LINUX_DEFAULT="nohz=on nohz_full="8-15 kthread_cpus=0-7 irqaffinity=0-7 isolcpus=domain,managed_irq,8-15"
```
(this assumes that cores 0-7 are left to system and 8-15 are reserved for benchmarks).
The run
```
$ sudo update-grub
```
and reboot.

You can now use `taskset 0xff00 ...` to run benchmarks on reserved cores.

# Run in non-GUI mode

To boot to non-GUI mode on systemd systems see https://linuxconfig.org/how-to-disable-enable-gui-in-ubuntu-22-04-jammy-jellyfish-linux-desktop
(`sudo init 1` otherwise).

# Fix frequency

Disable frequency scaling (and HW prefetching) in BIOS if possible and
set scaling governor to `performance`.
