#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Naver, Seznam, ...) which pages changed.

Reads the LIVE sitemap after deploy and submits URLs whose <lastmod> is within
--days (default 2), plus the machine-readable indexes when anything changed.
The key is public by design: it is served at /<key>.txt to prove ownership.

Usage: python3 scripts/indexnow.py [--days N] [--all] [--dry-run]
"""
import argparse
import datetime as dt
import json
import pathlib
import sys
import urllib.request
import xml.etree.ElementTree as ET

SITE = "https://blog.seolcu.com"
HOST = "blog.seolcu.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
UA = "seolcu-blog-indexnow/1.0"

ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=2)
ap.add_argument("--all", action="store_true", help="submit every sitemap URL")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

keys = sorted((pathlib.Path(__file__).resolve().parent.parent / "static").glob("*.txt"))
keys = [k for k in keys if len(k.stem) == 32 and k.read_text().strip() == k.stem]
if len(keys) != 1:
    sys.exit(f"indexnow: expected exactly one static/<key>.txt, found {len(keys)}")
key = keys[0].stem


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


if get(f"{SITE}/{key}.txt").decode().strip() != key:
    sys.exit("indexnow: live key file does not match; deploy first")

cutoff = dt.date.today() - dt.timedelta(days=args.days)
urls = []
for u in ET.fromstring(get(f"{SITE}/sitemap.xml")).findall("sm:url", NS):
    loc = u.findtext("sm:loc", namespaces=NS)
    lastmod = u.findtext("sm:lastmod", namespaces=NS)
    if args.all or (lastmod and dt.date.fromisoformat(lastmod[:10]) >= cutoff):
        urls.append(loc)

if not urls:
    print("indexnow: nothing changed recently; not submitting")
    sys.exit(0)
urls += [f"{SITE}/llms.txt", f"{SITE}/llms-full.txt", f"{SITE}/index.json"]
urls = sorted(set(urls))

payload = {"host": HOST, "key": key, "keyLocation": f"{SITE}/{key}.txt", "urlList": urls}
print(f"indexnow: {len(urls)} url(s)")
for u in urls:
    print("  " + u)
if args.dry_run:
    sys.exit(0)

req = urllib.request.Request(
    ENDPOINT,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": UA},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"indexnow: HTTP {r.status}")
except urllib.error.HTTPError as e:
    # 200/202 = accepted. 4xx means a key/host problem worth seeing, but never fail the deploy over it.
    print(f"::warning::indexnow: HTTP {e.code} {e.read()[:200]!r}")
