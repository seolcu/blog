---
title: "Don't pass credential-bearing URLs on the command line: they are readable in `ps` and `/proc/<pid>/cmdline`"
summary: "A pre-authenticated upload URL passed as a `curl` argument was visible to every local user for the whole multi-minute upload. Feed secrets to curl on stdin with `--config -` (or from a 0600 file) instead of argv."
date: 2026-11-09
status: working
verified_at: 2026-08-05
verified_how: "Found during a review of a backup uploader on Ubuntu 24.04 (OCI pre-authenticated request URL); fixed and the URL revoked the same minute."
applies_to:
  OS: "Linux (any; /proc/<pid>/cmdline is world-readable unless hidepid is set)"
  tool: "curl 8.x"
keywords:
  - "/proc/pid/cmdline secret"
  - "curl --config -"
  - "pre-authenticated request leak"
  - "ps aux token visible"
---

## Problem

```bash
curl -T backup.tar.gz "https://objectstorage.example.com/p/SECRET-TOKEN/n/ns/b/bucket/o/latest.tar.gz"
```

While the command runs, any local user can read the whole URL, token included:

```bash
ps -eo args | grep objectstorage
cat /proc/$(pgrep -n curl)/cmdline | tr '\0' ' '
```

A 3 GB upload kept the token visible for several minutes every night.

## Fix

Give curl the URL through its config syntax on stdin:

```bash
printf 'url = "%s"\n' "$UPLOAD_URL" | curl --config - -T backup.tar.gz --fail --silent --show-error
```

Or keep it in a root-only file: `curl --config /etc/<job>/upload.curlrc` (mode `0600`).

The same applies to `Authorization` headers: use `-H @file` (curl 7.55+) or put `header = "..."` in the config.

## Also

- Mounting `/proc` with `hidepid=2` hides other users' processes. It is a mitigation, not a fix: root and same-user processes still see them.
- Revoke the credential when you retire the workload that used it, in the same change.
