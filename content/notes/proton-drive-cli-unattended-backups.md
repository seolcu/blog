---
title: "Unattended offsite backups with the official Proton Drive CLI"
summary: "Run the official `proton-drive` CLI from systemd on headless servers: log hosts in as a separate editor account (Proton has no scoped tokens), store the session in `pass` with a passphrase-less GPG key, set a readable working directory, and purge the owner's trash yourself."
date: 2026-11-09
status: working
verified_at: 2026-11-09
verified_how: "Running in production since 2026-10-02 on four Ubuntu 24.04 / Debian 13 hosts (x86_64 and arm64), daily and weekly uploads of 1 MB–4.4 GB archives."
applies_to:
  proton-drive CLI: "0.8.0 (linux-x64, linux-arm64)"
  OS: "Ubuntu 24.04 LTS, Debian 13"
  init: "systemd"
keywords:
  - "proton-drive auth login"
  - "PROTON_DRIVE_CREDENTIALS_STORE=pass"
  - "EACCES"
  - "Trashed node not found"
  - "Wrong key usage"
  - "rclone protondrive"
---

## Summary

The official Proton Drive CLI works for unattended server backups, but four things are not obvious from its help text:

1. **Any CLI session is a full-account session.** Proton has no scoped tokens, app passwords or service accounts. Do not log servers in with your main account.
2. **Use a second (free) account as an *editor* of one shared folder.** Files it uploads are owned by, and counted against, the folder owner.
3. **The session store needs `pass`, and `pass` needs a GPG key that an unattended job can decrypt.** Give root a passphrase-less key and rely on file permissions.
4. **An editor's deletions land in the owner's trash, and Proton never empties trash on its own.** Something holding the owner's session has to purge it.

## Environment

- Proton Drive CLI `0.8.0` from <https://proton.me/download/drive/cli/> (MIT). Verify the SHA-512 on that index page before installing.
- Hosts: Ubuntu 24.04 LTS and Debian 13, x86_64 and arm64.
- Jobs run as root from systemd services.

## Account model

| Machine | Logged-in account | Can do |
|---|---|---|
| Backup hosts | secondary account, **editor** on `/my-files/<folder>` only | upload, list, trash inside that folder |
| One private helper host | main account (owner) | everything; used only to purge trash |

A compromised backup host can read and trash backups, nothing else: not mail, not Pass, not personal Drive files.

Verified: after a 4.1 GB upload by the editor account, the editor account's own storage usage still read 0. The upload counted against the owner.

Paths as each side sees them:

- Editor (hosts): `/shared-with-me/<folder>/<service>/<archive>`
- Owner: `/my-files/<folder>/<service>/<archive>`

## Install on a host

```bash
# CLI (check the sha512 first)
sudo install -m 0755 proton-drive /usr/local/bin/proton-drive

# pass without recommends; with recommends Debian/Ubuntu pull ~80 X11/Mesa packages
sudo apt-get install -y --no-install-recommends pass

# Passphrase-less GPG key for root, then initialise pass with it
sudo -H bash -c 'cd /root && gpg --batch --pinentry-mode loopback --passphrase "" \
  --quick-gen-key "backup proton <root@$(hostname)>" default default never \
  && pass init "$(gpg --list-secret-keys --with-colons | awk -F: "/^fpr/{print \$10; exit}")"'

# Log in as the SECONDARY account; open the printed URL in any browser
sudo -H bash -c 'cd /root && PROTON_DRIVE_CREDENTIALS_STORE=pass proton-drive auth login'

# First time only: accept the share invitation
sudo -H bash -c 'cd /root && PROTON_DRIVE_CREDENTIALS_STORE=pass proton-drive invitation list'
sudo -H bash -c 'cd /root && PROTON_DRIVE_CREDENTIALS_STORE=pass proton-drive invitation accept <id>'
```

## systemd unit essentials

```ini
[Service]
Type=oneshot
Environment=PROTON_DRIVE_CREDENTIALS_STORE=pass
Environment=HOME=/root
WorkingDirectory=/root
ExecStart=/usr/local/sbin/offsite-upload.sh
```

`HOME` and `WorkingDirectory` are required. `proton-drive` spawns `pass` from its current working directory, and the run fails with `EACCES` if that directory is not readable by the user.

## Upload, prune, restore

```bash
export PROTON_DRIVE_CREDENTIALS_STORE=pass
proton-drive filesystem upload -f skip ./world-20261002-032715.tar.gz /shared-with-me/homelab/minecraft/
proton-drive filesystem list /shared-with-me/homelab/minecraft
proton-drive filesystem trash /shared-with-me/homelab/minecraft/world-20260901-031500.tar.gz
proton-drive filesystem download -f remove /shared-with-me/homelab/minecraft/<archive> /tmp
```

- Upload each archive **under its own dated name** so every run adds a generation. Overwriting a single `latest` object means one corrupt-but-valid backup replaces your only offsite copy.
- `-f skip` makes re-uploading the same archive a no-op success, so retries are safe.
- `-f` values differ by command. `upload` takes `create-new-revision`, `rename`, `replace`, `skip`; `download` takes `rename`, `remove`, `skip`.
- An editor can only `trash`. `filesystem delete` works only on items that are already in the trash: `filesystem trash <path>`, then `filesystem delete /trash/<name>`.

## Purging the owner's trash

The trash belongs to the owner, so the purge has to run with the owner's session. Run it on a private host with no public services. Rules that keep it from destroying personal data:

- Delete only files whose author is the editor account, whose name matches the archive pattern, and that were trashed more than N days ago (3 here). The grace period doubles as a recovery window if a host is compromised and trashes good backups.
- The CLI deletes trashed items **by name only**. A node UID path returns `Trashed node not found`. Skip any name that appears more than once in the trash.
- Never call `empty-trash`; the trash also holds the owner's personal files.

## Throughput (measured)

- 4.1 GB upload from x86_64 at home: 327 s (~13 MB/s).
- 4.2 GB upload on arm64: 723 s with a 370 MB peak RSS. The CLI streams; it does not buffer whole files.
- On a 100 Mbps home line, an unthrottled upload peaked at ~77 Mbps and caused 10–27% packet loss for other traffic on that host. Rate-limit uploads that share a residential uplink, for example with an nftables mark on the job's cgroup plus a `tc` htb class.

## Not working / rejected

- `gpg --quick-gen-key <uid> ed25519 sign,encrypt` fails with `Wrong key usage`, because ed25519 cannot encrypt. `default default` creates the ed25519 + cv25519 pair that `pass` needs.
- **rclone's `protondrive` backend** was rejected. It is reverse-engineered, and its uploads were broken from 2025-11 to 2026-03.
- **Parallel listings.** Four concurrent `filesystem list` calls crashed in the CLI's SQLite cache and silently left folders out of a recursive listing. Run listings one at a time. `filesystem size` on a folder is a quick completeness check.

## Failure visibility

An expired or revoked session is not silent only if you make it loud. Here the uploader touches a stamp file after each successful upload, and the service's update job refuses to run when the stamp is stale (see [Gate automatic updates on backup freshness](/notes/backup-freshness-gate-for-automatic-updates/)). The CLI's session lifetime was not documented at the time of writing.
