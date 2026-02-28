#!/bin/bash

# Stop unnecessary services which cause performance jitter

set -eu
set -x

UNITS=$(systemctl list-units --all --plain | awk '/^(apt-daily|dpkg|unattended-upgrades|update-notifier|cron|anacron|avahi|fwupd|man-db|snapd|irqbalance|cups|systemd-oomd|udisks2|logrotate)/{print $1}')
sudo systemctl mask $UNITS
