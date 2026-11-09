---
title: "gamesir-connect-linux — GameSir Connect (Cyclone 2 app and firmware updates) on Linux"
summary: "Repackages GameSir's official Windows-only GameSir Connect Electron app to run unmodified on Linux, including controller firmware updates: the vendor's JieLi upgrade DLL runs in a Unicorn x86 emulator with device I/O routed to SG_IO."
date: 2026-11-09
status: experimental
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/gamesir-connect-linux"
license: "MIT"
applies_to:
  device: "GameSir Cyclone 2 (USB 3537:100b and related IDs)"
  needs: "curl, 7z, unzip, node, npm, openssl, python3; a udev rule (70-gamesir.rules)"
keywords:
  - "GameSir Connect Linux"
  - "GameSir Cyclone 2 Linux firmware update"
  - "3537:100b"
  - "JieLi firmware upgrade Linux"
---

## What it does

`build.sh` downloads the official installer (verified against the sha512 in GameSir's `latest.yml`) and converts it on your machine. The repository contains no GameSir code.

| Part | How it is handled |
|---|---|
| Runtime | Same Electron as the original, 13.6.9 linux-x64 (sha256 verified) |
| node-hid | Official N-API prebuild, hidraw backend |
| usb-detection | JS replacement polling `/sys/bus/usb` (the prebuild has symbol mismatches with Electron 13.6.9) |
| ffi-napi | Stubbed (only used for Windows DLLs; segfaults against system libffi) |
| Firmware | Official `jl_firmware_upgrade_x86.dll` emulated with Unicorn; SCSI commands go to `SG_IO` |

## Install

```bash
./build.sh
sudo install -m644 70-gamesir.rules /etc/udev/rules.d/ \
  && sudo udevadm control --reload-rules && sudo udevadm trigger
gamesir-connect
```

Run `./build.sh` again when a new version is released; the app's built-in auto-update is disabled. Not affiliated with GameSir.
