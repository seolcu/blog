---
title: "WakeLink — let a trusted contact ring a loud alarm on your Android phone"
summary: "Android app plus self-hosted Go backend: someone you have mutually paired with can trigger a loud alarm on your phone even in silent or vibrate mode (no special permission), with end-to-end encrypted messages, voice and pictures, and delivery confirmation that it actually rang."
date: 2026-11-09
status: active
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/wakelink"
homepage: "https://wake.seolcu.com"
license: "MIT"
applies_to:
  platform: "Android 8.0+ (APK, not on Play Store)"
  stack: "Kotlin / Jetpack Compose app, Go backend, Firebase Cloud Messaging"
  latest release: "v0.5.1 (2026-10-28)"
keywords:
  - "wake someone up remotely android"
  - "alarm through silent mode android"
  - "remote alarm app"
---

## Key behaviours

- Rings through silent and vibrate mode, and before the first unlock after a reboot.
- Tells the sender whether the alarm actually rang and when it was stopped.
- Only mutually paired contacts can connect (invite codes); either side can stop it at any time.
- Names, messages, recordings and pictures are end-to-end encrypted to the receiver's phone; the server relays ciphertext only.
- The receiver controls the volume (optional gradual rise) and which sounds and pictures are allowed.
- English and Korean.

Download: <https://wake.seolcu.com/download> (always the latest release).
