---
title: "PickGak (픽각) — Overwatch hero pick helper"
summary: "Web app that recommends which Overwatch hero to pick this match from the map, enemy comp, your team, party and preferred heroes, using official stats for Korea (Nexon), Asia, the Americas and Europe collected daily, with matchup explanations from duel data. Does not touch the game client."
date: 2026-11-09
status: active
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/pickgak"
homepage: "https://pickgak.seolcu.com"
license: "GPL-3.0"
applies_to:
  modes: "Role queue 5v5 (default) and open queue 6v6"
  languages: "English, Korean"
keywords:
  - "overwatch counter pick tool"
  - "오버워치 픽 추천"
  - "overwatch hero recommendation"
  - "픽각"
---

## What it adds over stat sites

Tier lists and win rates per map and rank are available elsewhere. PickGak also takes into account the current enemy comp (counter-picks), your party (duo/trio compositions), your preferred heroes, and ban votes that protect your heroes. It explains each pick with per-hero matchups and synergies.

Hero search understands Korean initial consonants (`ㄹㅇ` → Reinhardt).
