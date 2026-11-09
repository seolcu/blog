---
title: "kitty terminal over SSH: 'xterm-kitty': unknown terminal type"
summary: "Remote hosts don't have kitty's terminfo, so `nano`, `less`, `tput` and line editing fail with `Error opening terminal: xterm-kitty.` and similar. Connect with `kitten ssh` (it copies the terminfo and sets up shell integration), or copy the terminfo once with `infocmp -a xterm-kitty | ssh host tic -x -o ~/.terminfo /dev/stdin`."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/kitty-ssh/"]
status: working
verified_at: 2026-11-09
verified_how: "Error messages reproduced verbatim with TERM=xterm-kitty on an Ubuntu 24.04 server without kitty terminfo (nano 7.2, less, tput). Fix commands checked against kitty's official ssh-kitten docs and FAQ on 2026-11-09; they were not re-run on that date because the verifying machine had no kitty installed."
applies_to:
  terminal: "kitty with the `kitten` command (ssh kitten auto shell integration since 0.25.0)"
  remote: "any host without the xterm-kitty terminfo entry; reproduced on Ubuntu 24.04 LTS"
keywords:
  - "'xterm-kitty': unknown terminal type."
  - "Error opening terminal: xterm-kitty."
  - "tput: unknown terminal \"xterm-kitty\""
  - "WARNING: terminal is not fully functional"
  - "kitten ssh"
---

## Symptom

After `ssh` from kitty, programs on the remote side fail or misbehave. Messages reproduced on Ubuntu 24.04:

```
$ nano            ->  Error opening terminal: xterm-kitty.
$ less <file>     ->  WARNING: terminal is not fully functional
$ tput cols       ->  tput: unknown terminal "xterm-kitty"
```

Some shells and tools print `'xterm-kitty': unknown terminal type.` instead. Arrow keys and other function keys may also stop working.

## Cause

kitty sets `TERM=xterm-kitty`, and the remote host has no terminfo entry for it. Check on the remote host with `infocmp xterm-kitty`; it fails when the entry is missing.

## Fix

Use kitty's SSH kitten, a drop-in replacement for `ssh`. It copies the kitty terminfo database to the remote host and sets up shell integration there:

```bash
kitten ssh user@host
```

The official docs suggest a short alias:

```bash
alias s="kitten ssh"
```

To replace `ssh` itself, but only when you are actually inside kitty, add this to `~/.bashrc` or `~/.zshrc`:

```bash
[ "$TERM" = "xterm-kitty" ] && alias ssh="kitten ssh"
```

Older kitty releases documented the same kitten as `kitty +kitten ssh`.

## Alternatives

- Copy the terminfo once per remote host (from kitty's docs, "Copying terminfo files manually"):
  ```bash
  infocmp -a xterm-kitty | ssh myserver tic -x -o ~/.terminfo /dev/stdin
  ```
- If the distribution packages it, install `kitty-terminfo` on the remote host.
- For `sudo` on the remote host, keep the variables with `Defaults env_keep += "TERM TERMINFO"` (via `sudo visudo`).
- Fall back for one session: `TERM=xterm-256color ssh user@host`. You lose kitty-specific features.

Sources: <https://sw.kovidgoyal.net/kitty/kittens/ssh/>, <https://sw.kovidgoyal.net/kitty/faq/>
