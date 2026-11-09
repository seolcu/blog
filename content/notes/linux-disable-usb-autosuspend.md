---
title: "Disable USB autosuspend on Linux (USB Ethernet adapter drops after boot)"
summary: "Add the kernel parameter `usbcore.autosuspend=-1` and regenerate the bootloader config (`update-grub` on Debian/Ubuntu, `grubby` on Fedora). Verify with `cat /sys/module/usbcore/parameters/autosuspend` → `-1`."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/disable-usb-suspend/"]
status: working
verified_at: 2025-10-11
verified_how: "Laptop used as a server with a USB Ethernet dongle (no built-in LAN port), Debian-family OS with GRUB; the network stayed up across reboots after the change."
applies_to:
  OS: "Linux with GRUB (Debian/Ubuntu: update-grub; Fedora/RHEL: grubby)"
  kernel: "any (usbcore module parameter)"
keywords:
  - "usbcore.autosuspend=-1"
  - "usb ethernet adapter stops working after reboot"
  - "/sys/module/usbcore/parameters/autosuspend"
  - "power/control auto"
---

## Symptom

A laptop used as a server reaches the network through a USB Ethernet adapter. After a reboot the adapter sometimes stops passing traffic, because the kernel autosuspended the USB device.

## Fix (persistent, all USB devices)

Debian / Ubuntu:

```bash
sudoedit /etc/default/grub
# append to the existing value:
# GRUB_CMDLINE_LINUX_DEFAULT="quiet usbcore.autosuspend=-1"
sudo update-grub
sudo reboot
```

Fedora / RHEL:

```bash
sudo grubby --update-kernel=ALL --args="usbcore.autosuspend=-1"
sudo reboot
```

## Verify

```bash
cat /sys/module/usbcore/parameters/autosuspend   # expect: -1
cat /proc/cmdline                                # contains usbcore.autosuspend=-1
```

## Alternatives

- Without rebooting, for one device: `echo on | sudo tee /sys/bus/usb/devices/<bus-port>/power/control`. Find `<bus-port>` with `lsusb -t` or under `/sys/bus/usb/devices/*/product`. This does not survive a reboot. To make it persistent, add a udev rule matching the adapter's `idVendor`/`idProduct` with `ATTR{power/control}="on"`.
- Writing `-1` to `/sys/module/usbcore/parameters/autosuspend` at runtime only affects devices connected afterwards.

## Not working

- If TLP or `powertop --auto-tune` is installed, it can turn autosuspend back on. For TLP, set `USB_AUTOSUSPEND=0` or add the device to `USB_DENYLIST`.
