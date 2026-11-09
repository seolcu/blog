---
title: "Tidy — automatically sort a Samsung Galaxy (One UI) apps screen into folders"
summary: "Android app that organizes the real One UI Home apps screen into folders for you, on-device, with preview and undo. It knows Korean apps (Toss, Baemin, KakaoTalk) and Samsung apps."
date: 2026-11-09
status: experimental
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/tidy"
license: "MIT"
applies_to:
  device: "Samsung Galaxy with One UI Home, Android 10+"
  permission: "Accessibility service (used only on the One UI home screen, only while organizing)"
  latest release: "v0.2.0 (2026-10-22)"
keywords:
  - "one ui auto folder apps"
  - "galaxy app drawer organize automatically"
  - "갤럭시 앱 폴더 자동 정리"
---

## Modes

- **Keep my folders**: apps outside folders are moved into the folder they belong to; existing folders stay as they are.
- **Leave it to Tidy**: ignores existing folders and sorts every app from scratch.
- Every change is previewed first and can be undone. Newly installed apps can be filed automatically.
- The app list never leaves the phone.

If the Accessibility switch is greyed out: App info → ⋮ → Allow restricted settings.
