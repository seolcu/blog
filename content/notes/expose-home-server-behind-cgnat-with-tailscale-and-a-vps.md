---
title: "Expose a home server behind CGNAT through a VPS over Tailscale (Caddy for HTTPS, HAProxy for TCP)"
summary: "Without opening anything at home: put the home server and a public VPS on one tailnet, terminate HTTPS on the VPS with Caddy `reverse_proxy` to the server's MagicDNS name, and forward raw TCP (game ports) with HAProxy in `mode tcp`. Do public-side rate limiting on the VPS, because the backend only sees the VPS's tailnet IP."
date: 2026-11-09
status: working
verified_at: 2026-11-09
verified_how: "In production since 2026: Oracle Cloud Always Free arm64 VM as edge, x86_64 home server on a CGNAT ISP line, serving HTTPS sites and a Minecraft server."
applies_to:
  edge VM: "Ubuntu 24.04 LTS (Oracle Cloud Always Free, arm64)"
  home server: "Ubuntu 24.04 LTS, x86_64, behind CGNAT"
  tools: "Tailscale, Caddy 2, HAProxy 2.8"
keywords:
  - "CGNAT port forwarding alternative"
  - "tailscale reverse proxy vps"
  - "caddy reverse_proxy tailscale magicdns"
  - "haproxy mode tcp minecraft"
  - "self-host without port forwarding"
---

## Summary

```
Internet ──► VPS public IPv4 (Caddy :443, HAProxy :25565) ──tailnet──► home server
```

- The home router has **no port forwards** and the home server accepts no inbound traffic from the internet. Only the VPS has public ports.
- HTTPS: Caddy on the VPS gets certificates automatically and runs `reverse_proxy http://<home-magicdns-name>:<port>`.
- Non-HTTP TCP (game servers): HAProxy `mode tcp` frontend → `server <tailnet-ip>:<port> check`.
- SSH to every machine stays on the `tailscale0` interface only.

## Edge: Caddy

```caddyfile
media.example.com {
  encode zstd gzip
  reverse_proxy http://homeserver:8096
}
map.example.com {
  encode zstd gzip
  reverse_proxy http://homeserver:8100
}
```

`homeserver` resolves through Tailscale MagicDNS. On the home side, prefer having the app listen on `127.0.0.1` and publishing it to the tailnet with `tailscale serve`, or bind it to the tailscale IP. Avoid a broad `0.0.0.0` Docker port bind.

## Edge: HAProxy for TCP

```haproxy
defaults
  mode tcp
  option tcplog
  timeout connect 10s
  timeout client  4h
  timeout server  4h

frontend minecraft_tcp
  bind *:25565
  default_backend minecraft_backend

backend minecraft_backend
  server home_mc 100.x.y.z:25565 check
```

The long client/server timeouts keep idle game sessions from being cut off. Validate the config before reloading: `sudo haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy`.

## Firewalls (both layers)

On Oracle Cloud, a port must be opened in the VCN **security list** *and* in the VM's host firewall (`ufw allow 443/tcp`, etc.). Opening only one of them looks like a dead service.

## Rate limiting has to happen on the edge

Behind the proxy, the home server's `sshd`, `fail2ban` and application logs see only the edge's tailnet IP. OpenSSH does not support the PROXY protocol, so it cannot learn the real client address. Do per-source limiting on the edge:

```haproxy
frontend sftp_tcp
  bind *:2022
  stick-table type ip size 100k expire 1h store conn_rate(1m),gpc0
  tcp-request connection track-sc0 src
  tcp-request connection reject if { sc0_get_gpc0 gt 0 }
  tcp-request connection sc-inc-gpc0(0) if { sc0_conn_rate gt 10 }
  tcp-request connection reject if { sc0_conn_rate gt 10 }
  default_backend sftp_backend
```

A source that opens more than 10 connections per minute is flagged and rejected until it has been silent for 1 h.

## When *not* to proxy: games that register their public IP

Some game servers (for example Don't Starve Together via Klei's lobby) advertise the public IP they register *from*. Behind a DNAT hop, the lobby lists an address that is not the one being forwarded, and players cannot join. Run such servers directly on a cloud VM with their UDP ports open there.

## Not working / rejected

- **frp** (fatedier/frp) as the tunnel: it works (see [the frp note](/notes/frp-expose-local-server/)), but it is one more daemon and token to manage when the machines are already on a tailnet.
- **Tailscale subnet router + nginx-proxy-manager in Docker**: every new port needed a VPS firewall change, a Docker port change and a rebuild, plus a UI entry. Plain Caddy/HAProxy config files are easier to keep in version control.
- **Cloudflare Tunnel**: HTTP(S) only on the free path; it does not carry arbitrary TCP game traffic for players without a client.
