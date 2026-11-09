---
title: "Expose local TCP services without port forwarding using frp (frps on a VPS, frpc at home)"
summary: "Run `frps` on a public VPS (`bindPort = 7000`, `auth.token`) and `frpc` on any machine at home with one `[[proxies]]` block per service (`type = \"tcp\"`, `localIP`, `localPort`, `remotePort`). Both run as systemd services."
date: 2025-10-11
lastmod: 2026-11-09
aliases: ["/posts/how-to-use-frp/"]
status: archived
verified_at: 2025-10-11
verified_how: "frp 0.65.0 on an arm64 VPS (frps) and an arm64 Raspberry Pi (frpc) forwarding game servers. The author later moved to a Tailscale + Caddy/HAProxy setup and no longer runs frp."
superseded_by: "/notes/expose-home-server-behind-cgnat-with-tailscale-and-a-vps"
applies_to:
  frp: "0.65.0 (TOML config)"
  arch: "linux_arm64 release tarball (use linux_amd64 on x86_64)"
keywords:
  - "frps.toml"
  - "frpc.toml"
  - "frp systemd service"
  - "CGNAT port forwarding alternative"
---

## When to use it

frp is a self-hosted alternative to ngrok. It works behind CGNAT, carries arbitrary TCP and UDP (unlike the free Cloudflare Tunnel path), and the client can forward to any LAN address. So one small box at home (for example a Raspberry Pi) can expose services running on other machines. If your machines are already on a tailnet, see the [Tailscale + Caddy/HAProxy note](/notes/expose-home-server-behind-cgnat-with-tailscale-and-a-vps/) instead.

## Server (VPS)

```bash
V=0.65.0; A=linux_arm64     # or linux_amd64
wget https://github.com/fatedier/frp/releases/download/v$V/frp_${V}_$A.tar.gz
tar -xzf frp_${V}_$A.tar.gz
sudo install -m 0755 frp_${V}_$A/frps /usr/bin/frps
sudo install -d /etc/frp
```

`/etc/frp/frps.toml`:

```toml
bindPort = 7000
auth.token = "<long random secret>"
```

Without `auth.token`, anyone can attach a client to your server.

Test it with `frps -c /etc/frp/frps.toml`; the expected output includes `frps tcp listen on 0.0.0.0:7000` and `frps started successfully`. Then create `/etc/systemd/system/frps.service`:

```ini
[Unit]
Description=FRP Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=nobody
Restart=on-failure
RestartSec=5s
ExecStart=/usr/bin/frps -c /etc/frp/frps.toml
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now frps
```

Open `7000/tcp` and every `remotePort` in the VPS firewall *and* in the cloud provider's security list.

## Client (home)

Install `frpc` the same way. `/etc/frp/frpc.toml`:

```toml
serverAddr = "<vps public address>"
serverPort = 7000
auth.token = "<same secret as frps>"

[[proxies]]
name = "minecraft"
type = "tcp"
localIP = "192.168.1.101"
localPort = 25565
remotePort = 25565

[[proxies]]
name = "terraria"
type = "tcp"
localIP = "192.168.1.102"
localPort = 7777
remotePort = 7777
```

`/etc/systemd/system/frpc.service`:

```ini
[Unit]
Description=FRP Client
After=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/bin/frpc -c /etc/frp/frpc.toml
ExecReload=/usr/bin/frpc reload -c /etc/frp/frpc.toml
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now frpc
```

## If it doesn't connect

Check, in this order: the VPS firewall and security list for `7000` and each `remotePort`; that `auth.token` matches on both sides; that `localIP:localPort` is reachable from the frpc host; then `journalctl -u frpc -u frps`.

## Why the author moved away

frp is one more daemon and one more shared secret. Once every machine was on Tailscale anyway, Caddy and HAProxy on the VPS pointing at tailnet addresses did the same job with config files that are easier to keep in version control.
