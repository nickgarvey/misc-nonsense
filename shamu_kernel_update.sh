#!/bin/bash
set -ex

HTML_TMP=$(mktemp)
curl -s 'https://kernels.franco-lnx.net/Nexus6/7.1.1/anyKernel/' > "$HTML_TMP"

KERNEL_FILE=$(grep -oe 'fk-[^"]*zip' $HTML_TMP | tail -n1)
[[ "$KERNEL_FILE" =~ fk-r[0-9]{2,3}-anykernel2.zip ]] || exit

mkdir -p /tmp/phone_kernels
curl -s "https://kernels.franco-lnx.net/Nexus6/7.1.1/anyKernel/$KERNEL_FILE" > "/tmp/phone_kernels/$KERNEL_FILE"
adb push /tmp/phone_kernels/$KERNEL_FILE /sdcard/

echo "Enter to reboot phone"
read
adb reboot recovery
