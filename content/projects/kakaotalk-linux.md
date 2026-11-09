---
title: "kakaotalk-linux — KakaoTalk on Linux (Proton-based installer)"
summary: "Unofficial installer that runs the official Windows KakaoTalk on Linux through umu-launcher + GE-Proton (no Steam needed), with native tray menus, the desktop file picker, an emoji/Korean-IME Wine patch, and a fix for slow logins on public Wi-Fi."
date: 2026-11-09
status: experimental
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/kakaotalk-linux"
license: "MIT (patched Wine modules: LGPL-2.1+)"
applies_to:
  tested on: "Fedora 44, GNOME (fresh install, login, tray, attachments, emoji, Korean input)"
  needs: "x86_64, python3, curl, tar, Korean fonts; GNOME needs the AppIndicator extension for the tray"
  latest release: "v0.2.0 (2026-11-06)"
keywords:
  - "카카오톡 리눅스"
  - "KakaoTalk Linux"
  - "kakaotalk wine 한글 입력"
  - "kakaotalk proton"
  - "카카오톡 우분투 설치"
---

## What it solves

KakaoTalk has no Linux client. This tool downloads Kakao's official installer, installs it into your home directory (no root, about 1.4 GB of downloads), and makes it behave like a desktop app:

| Feature | Detail |
|---|---|
| Tray | Uses the desktop's own tray menu (on GNOME: click opens the menu, double-click opens the window) |
| File picker | Native desktop file chooser for attachments and saving |
| Slow login fix | Clears Wine's accumulated audio device list before launch (slow logins on public Wi-Fi) |
| Emoji / Korean IME patch | Emoji render instead of boxes; jamo appear while composing |
| No Steam | Runs through umu-launcher + GE-Proton |

## Install

```bash
git clone https://github.com/seolcu/kakaotalk-linux.git
cd kakaotalk-linux
./install.sh
```

Remove it with `./uninstall.sh`. This also deletes the chat data stored on that PC.

## Known limitations

- Emoji are monochrome and flags show as two letters (KakaoTalk draws with GDI, which cannot render color fonts).
- KakaoTalk's own message view and notifications cannot be restyled to match the system.
- If someone else's Mac shows up as an audio output on public Wi-Fi, that is PipeWire's AirPlay (RAOP) discovery. Put `context.properties = { module.raop = false }` in `~/.config/pipewire/pipewire.conf.d/90-disable-raop.conf` and log in again.

Not affiliated with Kakao. KakaoTalk itself is not modified or redistributed.
