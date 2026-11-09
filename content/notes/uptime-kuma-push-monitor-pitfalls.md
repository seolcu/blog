---
title: "Uptime Kuma push monitors: 24.8-day interval limit and the always-DOWN query string"
summary: "Uptime Kuma push intervals cannot exceed 2147483 s (~24.8 days, Node.js 32-bit timer). Monitor longer cadences with a weekly re-push of the last result. Also push to the bare `/api/push/<token>` URL: pasting the UI's `?status=up&msg=OK&ping=` URL and adding your own `status` makes every heartbeat record as DOWN."
date: 2026-11-09
status: working
verified_at: 2026-11-09
verified_how: "Observed and fixed on a self-hosted Uptime Kuma 2.x (Docker `louislam/uptime-kuma:2`) with ~30 monitors in production."
applies_to:
  Uptime Kuma: "2.x (Docker image louislam/uptime-kuma:2)"
  Node.js: "any (setTimeout limit is 2^31-1 ms)"
keywords:
  - "TimeoutOverflowWarning"
  - "push monitor interval"
  - "/api/push/"
  - "status=up&msg=OK&ping="
  - "heartbeat always down"
---

## Summary

| Problem | Cause | Fix |
|---|---|---|
| A job that runs monthly can't be watched by a push monitor | Interval max is `2147483` s (~24.8 days) | Weekly re-push of the last recorded result |
| Interval set above the max | `setTimeout` overflow: `TimeoutOverflowWarning`, check fires every 1 ms | Keep intervals ≤ `2073600` s (24 days) |
| Every push records DOWN even when the job succeeded | Query string pasted from the UI plus your own `status=` sends `status` twice | Store the bare URL ending at the token |
| Monitor red on the dashboard, nobody alerted | Monitor has no notification attached | Audit `monitor_notification` |

## 1. The interval ceiling

Node.js timers use a signed 32-bit millisecond value: `floor(2147483647 / 1000) = 2147483` seconds ≈ 24.8 days. A push monitor with a larger interval emits `TimeoutOverflowWarning` and evaluates every 1 ms. Leave a margin and use at most `2073600` s (24 days).

### Monitoring jobs that run less often than every 24 days

A "first Sunday of the month" job runs 28–35 days apart, so every gap exceeds the ceiling. Raising the interval is not possible. Feed the monitor indirectly:

1. On success, the job touches a stamp file (for example `/var/lib/<x>/update/<service>.stamp`) and pushes `up`. On failure it pushes `down` and leaves the stamp alone.
2. A separate weekly timer re-pushes the verdict: `up` if the stamp is younger than the longest legitimate gap (35 days = 840 h), otherwise `down`. It also pushes `down` if the stamp is missing.
3. Set the monitor interval to 24 days.

The two pushers cannot contradict each other. A failed run leaves the stamp unadvanced, so the next weekly re-push is also `down`.

```bash
#!/usr/bin/env bash
# weekly re-push; KUMA_PUSH_URL comes from an env file kept out of git
set -Eeuo pipefail
stamp=/var/lib/homelab/update/bookstack.stamp
max_h=840
if [[ -e $stamp ]] && (( ( $(date +%s) - $(stat -c %Y "$stamp") ) / 3600 <= max_h )); then
  status=up; msg=last_update_ok
else
  status=down; msg=update_stale_or_missing
fi
curl -fsS -G --data-urlencode "status=$status" --data-urlencode "msg=$msg" "$KUMA_PUSH_URL" >/dev/null
```

## 2. Every heartbeat records as DOWN

The UI shows the push URL as `https://<kuma>/api/push/<TOKEN>?status=up&msg=OK&ping=`. If you store that whole string and your script appends its own `status=...`, the request carries `status` twice. Kuma's handler then compares an array with `"up"`, the comparison fails, and every push is recorded as DOWN, including the successful ones.

Store only `https://<kuma>/api/push/<TOKEN>` and add parameters with `curl -G --data-urlencode`.

`HTTP 200` from the push endpoint only means the token was accepted, not that the heartbeat was recorded as UP. Check the state that was actually recorded:

```bash
sudo python3 -c "
import sqlite3
c=sqlite3.connect('file:/path/to/data/kuma.db?mode=ro',uri=True)
for n,s,m in c.execute('''SELECT m.name,h.status,h.msg FROM monitor m
  LEFT JOIN heartbeat h ON h.id=(SELECT id FROM heartbeat WHERE monitor_id=m.id
  ORDER BY time DESC LIMIT 1) WHERE m.active=1 ORDER BY m.name'''):
    print(('UP' if s==1 else 'DOWN').ljust(6), n, m or '')"
```

## 3. Monitors without a notification

Marking a notification as "Default" only applies to monitors created *after* that. Existing monitors stay silent. In one incident, nine monitors (including every backup heartbeat) had no notification and stayed mute through an outage. Audit them; the query should return zero rows:

```bash
sudo docker exec uptime-kuma sqlite3 /app/data/kuma.db \
  "select m.id, m.name from monitor m
   where m.active = 1
     and not exists (select 1 from monitor_notification mn where mn.monitor_id = m.id);"
```

## Not working

- Setting the interval to 30 or 35 days "because the UI accepts it": it overflows, see section 1.
- Treating a 200 from `/api/push/` as proof that the monitor is UP: see section 2.
