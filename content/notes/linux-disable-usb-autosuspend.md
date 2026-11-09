---
title: "Disable USB autosuspend on Linux (USB Ethernet adapter drops after boot)"
summary: "Add the kernel parameter `usbcore.autosuspend=-1` and regenerate the bootloader config (`update-grub` on Debian/Ubuntu, `grubby` on Fedora). Verify with `cat /sys/module/usbcore/parameters/autosuspend` → `-1`, and check that the adapter's `power/runtime_status` reads `active`."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/disable-usb-suspend/"]
status: working
verified_at: 2026-11-09
verified_how: "Checked on a laptop home server whose only wired link is a Realtek RTL8153 USB adapter (`0bda:8153`, default route). Ubuntu 24.04, kernel 6.8.0-149-generic. Read back `/proc/cmdline`, the usbcore parameter and the adapter's sysfs power state after a reboot (all as below). The setting has been in use since 2025-10."
applies_to:
  OS: "Linux with GRUB (Debian/Ubuntu: update-grub; Fedora/RHEL: grubby); verified on Ubuntu 24.04 LTS"
  kernel: "any (usbcore module parameter); verified on 6.8.0-149-generic"
  hardware: "USB Ethernet adapters, e.g. Realtek RTL8153 (0bda:8153)"
keywords:
  - "usbcore.autosuspend=-1"
  - "usb ethernet adapter stops working after reboot"
  - "RTL8153 0bda:8153 autosuspend"
  - "/sys/module/usbcore/parameters/autosuspend"
  - "power/control auto"
---

## Symptom

A laptop used as a server reaches the network through a USB Ethernet adapter because it has no built-in LAN port. After a reboot the adapter sometimes stops passing traffic, because the kernel autosuspended the USB device.

## Fix (persistent, all USB devices)

Debian / Ubuntu:

```bash
sudoedit /etc/default/grub
# set or append to the existing value:
# GRUB_CMDLINE_LINUX_DEFAULT="usbcore.autosuspend=-1"
sudo update-grub
sudo reboot
```

Fedora / RHEL:

```bash
sudo grubby --update-kernel=ALL --args="usbcore.autosuspend=-1"
sudo reboot
```

## Verify

Output from the verified host:

```console
$ cat /proc/cmdline
BOOT_IMAGE=/vmlinuz-6.8.0-149-generic root=/dev/mapper/ubuntu--vg-ubuntu--lv ro usbcore.autosuspend=-1
$ cat /sys/module/usbcore/parameters/autosuspend
-1
$ d=$(dirname "$(grep -l 8153 /sys/bus/usb/devices/*/idProduct)")   # use your adapter's idProduct
$ cat $d/power/control $d/power/autosuspend_delay_ms $d/power/runtime_status
on
-1000
active
```

`runtime_status` is the one that matters: `active` means the device is not suspended. Other USB devices on the same host can still show `power/control` = `auto` while the parameter is `-1`. That is expected, because the parameter sets their default autosuspend delay to "never" (`-1000` ms) rather than changing `control`.

## Alternatives

- Without rebooting, for one device: `echo on | sudo tee /sys/bus/usb/devices/<bus-port>/power/control`. Find `<bus-port>` with `lsusb -t` or `grep -l <idProduct> /sys/bus/usb/devices/*/idProduct`. This does not survive a reboot. To make it persistent, add a udev rule matching the adapter's `idVendor`/`idProduct` with `ATTR{power/control}="on"`.
- Writing `-1` to `/sys/module/usbcore/parameters/autosuspend` at runtime only affects devices connected afterwards.

## Not working

- If TLP or `powertop --auto-tune` is installed, it can turn autosuspend back on. For TLP, set `USB_AUTOSUSPEND=0` or add the device to `USB_DENYLIST`. Neither was installed on the verified host.
