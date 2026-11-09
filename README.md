# blog.seolcu.com

Source of <https://blog.seolcu.com>: verified fixes and setup notes, plus an index of my projects. The site is written for AI agents first and people second, so every page is structured and states its status, the environment it was verified on, and the verification date.

## Layout

| Path | What |
|---|---|
| `content/notes/<id>.md` | One problem per page (schema below) |
| `content/projects/<repo>.md` | Project summary; the repo README stays canonical |
| `layouts/` | Minimal theme (no JS) plus machine outputs: `page.markdown.md` (each page as `index.md`), `home.llms.txt`, `home.llmsfull.txt`, `home.json.json`, `robots.txt` |
| `scripts/check.py` | Front-matter schema, leak patterns, build-output checks (run in CI) |

## Note schema

```yaml
---
title: "Problem stated the way someone would search for it"
summary: "The answer in one or two sentences (<= 400 chars)."
date: 2026-11-09
status: working            # working | broken | superseded | archived
verified_at: 2026-11-09    # last time the author confirmed it on the stated environment
verified_how: "What was run, where."
applies_to:                # exact versions
  OS: "Fedora 44"
keywords:                  # verbatim error strings and likely search terms
  - "exact error message"
superseded_by: "/notes/<id>"   # optional
aliases: ["/old/url/"]         # optional, for moved pages
---
## Summary / Symptom / Cause / Fix / Verify / Not working
```

Projects use `status: active | experimental | archived` and require `repo`.

Rules:

- Change `verified_at` only after actually re-checking the content. CI warns once it is older than `params.staleDays` (365).
- Never publish internal details: tailnet IPs/names, push tokens, keys, personal e-mail addresses. `scripts/check.py` blocks the common shapes; gitleaks runs in CI too.
- Don't duplicate a project README; summarize and link.

## Build locally

```bash
hugo server                       # Hugo 0.151.0
hugo --gc --minify && python3 scripts/check.py public
```

Deployed to GitHub Pages by `.github/workflows/site.yml` on push to `main`, and rebuilt weekly.

License: content CC BY 4.0, code MIT.
