---
title: "overwatch-nexon-linux-fix — Overwatch (Nexon KR) error 0xE01300B0 on Linux"
summary: "Fixes Overwatch failing to start under Proton/Wine since the 2026-08-12 Nexon transfer (Blizzard error 0xE01300B0, inner exception 0xC06D007E). Wine's crypt32 stops at a self-signed root instead of the cross-signed chain; the wrapper adds the cross-certificate to the prefix and hides that root from the game. Nothing is patched or disabled."
date: 2026-11-09
status: active
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/overwatch-nexon-linux-fix"
license: "MIT"
applies_to:
  verified: "Fedora 44, kernel 7.1.8, KDE Plasma Wayland; RX 7700 XT, Mesa 26.1.6; GE-Proton11-5 / Proton Experimental 11.0 (steamrt4); Battle.net as a non-Steam game"
  untested: "Lutris, Heroic, Bottles, plain wine (same mechanism)"
  needs: "bubblewrap, openssl, python3"
keywords:
  - "0xE01300B0"
  - "0xC06D007E"
  - "Overwatch has encountered a critical error during startup."
  - "설치한 파일에 문제가 있습니다"
  - "오버워치 넥슨 리눅스"
  - "Overwatch Nexon Proton"
  - "Steam Deck Overwatch Korea"
---

## Symptom

Overwatch launched from Battle.net shows a black window, then two dialogs:

```
Overwatch has encountered a critical error during startup.
Please reinstall the game and try again.
```

```
설치한 파일에 문제가 있습니다. 문제가 지속되면 게임을 다시 설치해 주십시오.
(0xE01300B0)
```

Reinstalling, Scan and Repair, changing Proton versions and clearing shader caches do not help. If the code in the dialog is not `0xE01300B0`, the cause is different.

## Cause

Since the transfer to Nexon, a game DLL is signed by NEXON Korea Corporation through a chain that Windows validates via a cross-certificate. Wine's `CertGetCertificateChain` stops at the first trusted self-signed root it finds and never considers the cross-signed path, so the signature check fails. In addition, `CertCreateCertificateChainEngine` does not implement `hExclusiveRoot` or `hRestrictedRoot`; both return `E_INVALIDARG`.

## Fix

```bash
git clone https://github.com/seolcu/overwatch-nexon-linux-fix.git
cd overwatch-nexon-linux-fix
./overwatch-nexon-linux-fix.sh install
```

Then set the Steam launch options of the Battle.net non-Steam shortcut to:

```
/full/path/overwatch-nexon-linux-fix.sh run %command%
```

`install` finds the prefix (Steam, Lutris, Bottles, Heroic, plain wine), backs up `system.reg`, and builds a trust list under `~/.local/share/overwatch-nexon-fix/certs`. The host trust store is not modified. The full analysis is in the repository's `docs/ANALYSIS.md`.
