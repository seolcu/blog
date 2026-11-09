#!/usr/bin/env python3
"""Validate content front matter, block leaks of private details, and check the built site.

Usage: python3 scripts/check.py [public_dir]
Exit 1 on errors; staleness is reported as GitHub Actions warnings only.
"""
import datetime as dt
import pathlib
import re
import sys
import tomllib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONFIG = tomllib.loads((ROOT / "hugo.toml").read_text())
STALE_DAYS = int(CONFIG["params"].get("staleDays", 365))

SCHEMA = {
    "notes": {
        "status": {"working", "broken", "superseded", "archived"},
        "required": ["title", "summary", "date", "status", "verified_at", "verified_how", "applies_to", "keywords"],
    },
    "projects": {
        "status": {"active", "experimental", "archived"},
        "required": ["title", "summary", "date", "status", "verified_at", "verified_how", "repo"],
    },
}

# Things that must never appear on a public page. Placeholders like 100.x.y.z or <TOKEN> are fine.
LEAKS = [
    (re.compile(r"\b100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b"), "Tailscale CGNAT-range IP"),
    (re.compile(r"\b[\w-]+\.ts\.net\b"), "tailnet MagicDNS domain"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"/api/push/(?!<)[A-Za-z0-9]{8,}"), "Uptime Kuma push token"),
    (re.compile(r"/p/(?!SECRET)[A-Za-z0-9+/_-]{20,}/n/"), "OCI pre-authenticated request"),
    (re.compile(r"\btskey-[A-Za-z0-9-]+"), "Tailscale auth key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"[\w.+-]+@(?:proton\.me|protonmail\.com|pm\.me|gmail\.com|passmail\.net)\b"), "personal e-mail address"),
]

errors: list[str] = []
warnings: list[str] = []


def front_matter(path: pathlib.Path) -> dict:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{path}: missing YAML front matter")
        return {}
    return yaml.safe_load(m.group(1)) or {}


def as_date(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return dt.date.fromisoformat(str(v)[:10])


today = dt.date.today()
for section, rule in SCHEMA.items():
    for path in sorted((CONTENT / section).glob("*.md")):
        if path.name == "_index.md":
            continue
        rel = path.relative_to(ROOT)
        fm = front_matter(path)
        for key in rule["required"]:
            if fm.get(key) in (None, "", [], {}):
                errors.append(f"{rel}: missing '{key}'")
        status = fm.get("status")
        if status and status not in rule["status"]:
            errors.append(f"{rel}: status '{status}' not in {sorted(rule['status'])}")
        if status == "superseded" and not fm.get("superseded_by"):
            errors.append(f"{rel}: status superseded needs 'superseded_by'")
        if sb := fm.get("superseded_by"):
            if not (CONTENT / (sb.strip("/") + ".md")).exists():
                errors.append(f"{rel}: superseded_by '{sb}' does not exist")
        if va := fm.get("verified_at"):
            try:
                age = (today - as_date(va)).days
                if age < 0:
                    errors.append(f"{rel}: verified_at is in the future")
                elif age > STALE_DAYS and status in ("working", "active"):
                    warnings.append(f"{rel}: verified {age} days ago (> {STALE_DAYS}); re-verify or change status")
            except ValueError:
                errors.append(f"{rel}: verified_at '{va}' is not YYYY-MM-DD")
        if len(str(fm.get("summary", ""))) > 400:
            errors.append(f"{rel}: summary longer than 400 characters")

for path in sorted(list(CONTENT.rglob("*.md")) + list((ROOT / "layouts").rglob("*")) + [ROOT / "hugo.toml"]):
    if not path.is_file():
        continue
    text = path.read_text(errors="replace")
    for n, line in enumerate(text.splitlines(), 1):
        for rx, what in LEAKS:
            if rx.search(line):
                errors.append(f"{path.relative_to(ROOT)}:{n}: looks like a {what}")

if len(sys.argv) > 1:
    public = pathlib.Path(sys.argv[1])
    for f in ("llms.txt", "llms-full.txt", "index.json", "robots.txt", "sitemap.xml"):
        if not (public / f).is_file():
            errors.append(f"build: {f} missing")
    for section in SCHEMA:
        for page in (public / section).glob("*/index.html"):
            if not (page.parent / "index.md").is_file():
                errors.append(f"build: {page.parent.relative_to(public)} has no index.md twin")
    for md in public.rglob("index.md"):
        if re.search(r"&(#\d+|lt|gt|amp|quot);", md.read_text()):
            errors.append(f"build: {md.relative_to(public)} contains HTML entities (template escaping)")

for w in warnings:
    print(f"::warning::{w}")
for e in errors:
    print(f"::error::{e}")
print(f"check: {len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
