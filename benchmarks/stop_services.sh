#!/bin/bash

# Stop unnecessary services which cause performance jitter

set -eu
set -x

sudo systemctl stop apt-daily* dpkg* unattended-upgrades* update-notifier* fwupd* snapd* irqbalance* cups* {systemd-oomd,udisks2,polkit}.service
