---
title: "Gate automatic updates on backup freshness (bash + systemd pattern)"
summary: "Let an unattended update job run only if a verified local backup and an offsite-upload stamp are both younger than a threshold; otherwise skip with exit 0 and push DOWN to a heartbeat monitor. A broken backup then surfaces as a red monitor instead of an update without a restore point."
date: 2026-11-09
status: working
verified_at: 2026-11-09
verified_how: "Pattern in production since 2026-07 for Docker Compose and game-server update jobs on Ubuntu 24.04 hosts."
applies_to:
  OS: "any Linux with systemd and GNU coreutils"
  shell: "bash 5"
keywords:
  - "update_skipped_gate"
  - "backup freshness check before update"
  - "latest.tar.gz symlink"
  - "OnSuccess="
  - "tar -tzf verify"
---

## Summary

Three layers per service, coupled by file timestamps rather than by a scheduler:

1. **Backup** writes `daily/<name>-YYYYMMDD-HHMMSS.tar.gz`, verifies it with `tar -tzf`, and only then repoints `latest.tar.gz` at it. On failure it deletes the new archive and exits non-zero.
2. **Offsite upload** runs from `OnSuccess=` on the backup unit, uploads what `latest.tar.gz` points at, then touches `<service>.stamp`.
3. **Update** checks that both `latest.tar.gz` (through the symlink) and the stamp are younger than N hours. If either is missing or stale it **skips** (exit 0) and pushes `down` to an Uptime Kuma push monitor.

The safety property comes down to one rule: **never repoint `latest.tar.gz` at an archive you have not verified.** A failed backup leaves the symlink on the last good archive, its mtime grows old, the gate trips, and the monitor turns red.

## Why skip instead of fail

A failed unit is easy to miss, and `OnFailure=` handlers are easy to misconfigure. A skip that pushes DOWN shows up on the same dashboard and in the same alert channel as every other monitor, and it never updates a service that has no recent restore point.

## Gate implementation

```bash
# shared lib, sourced by every update script
file_age_hours() { echo $(( ( $(date +%s) - $(stat -c %Y "$1") ) / 3600 )); }

skip_gate() {
  logger -t "update[$SERVICE_NAME]" "update_skipped_gate reason=$1"
  push_status down "skipped_gate:$1"
  exit 0
}

require_recent_file() {   # path max_hours label
  [[ -e $1 ]] || skip_gate "${3}_missing"
  local age; age=$(file_age_hours "$1")
  (( age <= $2 )) || skip_gate "${3}_stale_${age}h"
  logger -t "update[$SERVICE_NAME]" "gate_ok gate=$3 age_h=$age max_h=$2"
}

run_freshness_gates() {
  require_recent_file "$BACKUP_PATH" "$MAX_BACKUP_AGE_HOURS" backup
  require_recent_file "$OFFSITE_STAMP_PATH" "$MAX_OFFSITE_AGE_HOURS" offsite
}

trap 'logger -t "update[$SERVICE_NAME]" "update_failed line=$LINENO"; push_status down failed' ERR
```

`stat -c %Y` follows symlinks, so `BACKUP_PATH=/opt/backups/<svc>/daily/latest.tar.gz` reads the mtime of the verified archive.

## Backup side

```bash
set -Eeuo pipefail
umask 027
out="/opt/backups/$svc/daily/$svc-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$out" -C /opt/services/$svc data
if ! tar -tzf "$out" >/dev/null; then rm -f "$out"; exit 1; fi
ln -sfn "$(basename "$out")" "/opt/backups/$svc/daily/latest.tar.gz"
```

When backing up a live directory, GNU tar exits `1` for "file changed as we read it" and `>=2` for fatal errors. Treat `1` as a warning if the data is quiesced (for example Minecraft `save-off` + `save-all flush` over RCON), and treat `>=2` as a failure.

## Retention pitfalls (both happened)

- **Pruning by age alone does not bound size.** Manual re-runs on the same day multiply the archives. Also cap by count.
- **Never delete the `latest.tar.gz` target**, even when it is the oldest file. A dangling symlink makes the gate skip forever.

## Units

```ini
# <svc>-backup.service
[Unit]
OnSuccess=offsite-upload.service

# <svc>-update.service
[Unit]
OnFailure=update-failure@%n.service
[Service]
Type=oneshot
EnvironmentFile=-/etc/default/<svc>-update   # holds KUMA_PUSH_URL, kept out of git
ExecStart=/usr/local/sbin/<svc>-update.sh
```

Schedule the update timer well after the backup and upload normally finish, and set both age thresholds above the backup cadence (24 h for daily backups, about 8 days for weekly ones).

## Log markers

Emit exactly one of `update_ok`, `update_failed` or `update_skipped_gate` per run, as `key=value` lines. Monitors and `journalctl -g` searches can then rely on them.
