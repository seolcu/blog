---
title: "GitHub Sponsor button not showing despite FUNDING.yml: enable `hasSponsorshipsEnabled` per repository"
summary: "A `FUNDING.yml` (per repo or in your account's `.github` repo) is not enough. Each repository also needs its Sponsorships feature turned on, either under Settings → General → Features → Sponsorships or in bulk with the GraphQL `updateRepository(input: {hasSponsorshipsEnabled: true})` mutation. The REST repo object has no such field."
date: 2026-11-09
status: working
verified_at: 2026-11-09
verified_how: "On a personal account with a newly approved GitHub Sponsors profile: added `FUNDING.yml` to the account's `.github` repo, saw no button on 9 public repos, enabled the flag via GraphQL with gh 2.97.0, and confirmed the button in the repo pages' HTML."
applies_to:
  platform: "github.com, personal account with an approved GitHub Sponsors profile"
  tool: "GitHub CLI (gh) 2.97.0; GraphQL API"
keywords:
  - "FUNDING.yml sponsor button not showing"
  - "hasSponsorshipsEnabled"
  - "updateRepository sponsorships"
  - "enable sponsorships all repositories"
  - ".github FUNDING.yml default"
---

## Symptom

`FUNDING.yml` contains `github: <user>`, and your Sponsors profile is live, but repository pages show no **Sponsor** button and no "Sponsor this project" sidebar.

Repository GraphQL data already reports the funding link, which makes it look as if everything is configured:

```console
$ gh api graphql -f query='{ repository(owner:"seolcu", name:"kakaotalk-linux"){ hasSponsorshipsEnabled fundingLinks { platform url } } }' --jq .data
{"repository":{"fundingLinks":[{"platform":"GITHUB","url":"https://github.com/seolcu"}],"hasSponsorshipsEnabled":false}}
```

## Cause

Two settings are involved, and they are independent:

1. **Funding links:** `FUNDING.yml` in the repository, or a default in your account's public `.github` repository. The default applies to every repository that has no `FUNDING.yml` of its own.
2. **Display:** the per-repository Sponsorships feature, `hasSponsorshipsEnabled`. The GraphQL schema describes it as "Indicates if the repository displays a Sponsor button for financial contributions." Without it, the funding links are not displayed.

The REST repository object (`gh api repos/<owner>/<repo>`) has no sponsorship field, so you will not find it there. It is only in GraphQL and in the web UI.

## Fix

**One repository:** Settings → General → Features → check **Sponsorships**.

**One account-wide default for links:** create a public `<user>/.github` repository containing `FUNDING.yml`. The contents API can create that first commit even in an empty repository:

```bash
gh repo create <user>/.github --public -d "Default community health files"
gh api -X PUT repos/<user>/.github/contents/FUNDING.yml \
  -f message="Add GitHub Sponsors funding link" \
  -f content="$(printf 'github: <user>\n' | base64)"
```

**Display, in bulk via GraphQL:**

```bash
for r in repo-a repo-b repo-c; do
  id=$(gh api repos/<user>/$r --jq .node_id)
  gh api graphql -f id="$id" -f query='
    mutation($id: ID!) {
      updateRepository(input: {repositoryId: $id, hasSponsorshipsEnabled: true}) {
        repository { name hasSponsorshipsEnabled }
      }
    }' --jq '.data.updateRepository.repository | "\(.name) \(.hasSponsorshipsEnabled)"'
done
```

To cover every public, non-fork, non-archived repository instead of a fixed list:

```bash
gh repo list <user> --visibility public --no-archived --source --limit 200 --json name --jq '.[].name'
```

## Verify

```bash
gh api graphql -f query='{ repository(owner:"<user>", name:"<repo>"){ hasSponsorshipsEnabled } }' --jq .data
curl -s https://github.com/<user>/<repo> | grep -c 'Sponsor this project'   # >= 1 once displayed
```

In the verified run, all 9 repositories showed `0` from the `curl` check before the mutation and `1` right after it. No cache delay was observed.

## Notes

- New repositories pick up the account-wide `FUNDING.yml`, but you still have to enable `hasSponsorshipsEnabled` on each one.
- Enabling the flag on a repository that has no funding links (no repo or account `FUNDING.yml`) is expected to show nothing. This was not tested.
