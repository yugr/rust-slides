#!/bin/bash

# Stop unnecessary services which cause performance jitter

set -eu
set -x

sudo systemctl stop apt-daily* unattended-upgrades* update-notifier* fwupd* snapd* irqbalance* {systemd-oomd,udisks2,polkit}.service
