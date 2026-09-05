#!/bin/bash
# If the phone tether is down (no enx* interface with an IPv4 address), ask the Android over ADB to turn USB tethering back on.
# Keeps the adb function alive (rndis,adb) so the next recovery still has a channel. Checks every 20 s.
A=/home/bo/bin/platform-tools/adb
up(){ ip -br -4 a | grep -qE "^enx.*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"; }
while true; do
  if ! up; then
    echo "$(date +%F_%T) tether down; asking phone"
    $A shell svc usb setFunctions rndis,adb 2>&1 | head -1
    for i in 1 2 3 4 5 6; do sleep 10; up && { echo "$(date +%F_%T) tether back"; break; }; done
    if ! up; then echo "$(date +%F_%T) still down; renewing dhcp"; sudo netplan apply 2>/dev/null; sleep 20; fi
    up || { echo "$(date +%F_%T) still down; retrying with rndis only"; $A shell svc usb setFunctions rndis 2>&1 | head -1; sleep 30; }
  fi
  sleep 20
done
