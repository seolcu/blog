---
title: "OCI Object Storage: versioning + fixed-key overwrites quietly bill terabytes"
summary: "With bucket versioning on, overwriting the same object name daily keeps every old copy as a noncurrent version. 3.26 GiB of current objects carried 1.78 TiB of versions and cost $29.93–$58.56/month. `oci os object bulk-delete` does not remove versions; delete by `version-id`."
date: 2026-11-09
status: archived
verified_at: 2026-07-02
verified_how: "Billing observed May–July 2026 on an Oracle Cloud tenancy using an Always Free Object Storage bucket for nightly backups; cleanup done 2026-07-02. The bucket was retired on 2026-10-02."
applies_to:
  service: "Oracle Cloud Infrastructure Object Storage"
  CLI: "oci-cli 3.x"
keywords:
  - "oci object storage unexpected cost"
  - "noncurrent object versions"
  - "oci os object list-object-versions"
  - "bulk-delete does not delete versions"
  - "always free 10GB exceeded"
---

## Summary

A backup job overwrote one object per service (`<service>/latest.tar.gz`) every night in a bucket that had **versioning enabled**. Each overwrite kept the previous object as a noncurrent version, and those versions are billed. The Always Free tier covers 10 GB in total, versions included.

| Month (2026) | Bill |
|---|---|
| May | $29.93 |
| June | $58.56 |
| July (after cleanup on 07-02) | $3.02 |

At cleanup time, 3.26 GiB of current objects carried 1.78 TiB of noncurrent versions.

## Diagnose

```bash
oci os bucket get --bucket-name <bucket> --query 'data.versioning'
oci os object list-object-versions --bucket-name <bucket> --all \
  --query 'length(data)'
```

The console's bucket size and `oci os object list` show only current objects, so they make the bucket look small.

## Fix

```bash
# 1) stop creating versions
oci os bucket update --bucket-name <bucket> --versioning Suspended

# 2) list every version, review the list, then delete the noncurrent ones by version-id
oci os object list-object-versions --bucket-name <bucket> --all > versions.json
jq -r '.data[] | [.name, ."version-id", ."time-modified"] | @tsv' versions.json | sort > versions.tsv
#    remove the newest row per object name from versions.tsv if you want to keep current objects, then:
while IFS=$'\t' read -r name ver _; do
  oci os object delete --bucket-name <bucket> --object-name "$name" --version-id "$ver" --force
done < versions.tsv
```

The loop is a sketch of the method that was actually used: list the versions, then delete them by `version-id`. Read `versions.tsv` before you delete anything. `oci os object bulk-delete` targets current object names only and leaves every version in place.

## Prevent

- Keep versioning off for fixed-key overwrite workloads, or add a lifecycle rule that deletes previous versions after N days.
- Create a budget alert on day one. A $1 alert would have caught this in May.
- Better yet, upload **dated** object names and prune them with your own retention. You get real generations instead of hidden ones.
