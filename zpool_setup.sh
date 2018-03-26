#!/bin/bash

if [[ $(hostname) != challenger ]]; then
	echo "Values are hard coded, don't run this on other hosts"
	exit 1
fi

zpool create zpool /dev/sdb
zfs set compression=zpool
zfs create zpool/backups
