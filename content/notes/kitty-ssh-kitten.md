---
title: "kitty terminal over SSH: 'xterm-kitty': unknown terminal type"
summary: "Remote hosts don't have kitty's terminfo, so editors, `less` and line editing break. Use `kitten ssh` (it copies the terminfo automatically) and alias `ssh` to it only when running inside kitty."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/kitty-ssh/"]
status: working
verified_at: 2025-10-11
verified_how: "kitty on a Linux desktop, SSH into Debian/Ubuntu servers with bash."
applies_to:
  terminal: "kitty (current versions ship the `kitten` binary; older ones use `kitty +kitten ssh`)"
  shell: "bash or zsh on the local machine"
keywords:
  - "'xterm-kitty': unknown terminal type."
  - "Error opening terminal: xterm-kitty."
  - "WARNING: terminal is not fully functional"
  - "kitten ssh"
---

## Symptom

After `ssh` from kitty, the remote side prints one of the following, or editors and the line editor misbehave:

```
'xterm-kitty': unknown terminal type.
Error opening terminal: xterm-kitty.
WARNING: terminal is not fully functional
```

## Cause

kitty sets `TERM=xterm-kitty`, and the remote host has no terminfo entry for it.

## Fix

Use kitty's SSH kitten. It copies the terminfo (and optionally shell integration) to the remote host:

```bash
kitten ssh user@host           # older kitty: kitty +kitten ssh user@host
```

To make it the default only inside kitty, add this to `~/.bashrc` (or `~/.zshrc`):

```bash
[ "$TERM" = "xterm-kitty" ] && alias ssh="kitten ssh"
```

Open a new terminal for the alias to take effect.

## Alternatives

- Install the terminfo once on the remote host: `infocmp -a xterm-kitty | ssh user@host tic -x -o ~/.terminfo /dev/stdin`
- Fall back for one session: `TERM=xterm-256color ssh user@host` (you lose kitty-specific features).
