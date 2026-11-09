---
title: "Mini-KVM — a small x86 hypervisor on the raw KVM API for kernel developers"
summary: "About 4,200 lines of C on the Linux KVM ioctl API that boot Multiboot/ELF kernels and a stock Linux kernel to a shell, render VGA text mode, and explain guest failures (faults, descriptor tables, page-table mappings, why it triple-faulted) instead of silently resetting."
date: 2026-11-09
status: experimental
verified_at: 2026-11-09
verified_how: "Summary checked against the repository README on 2026-11-09. Tested environments are those the README states."
repo: "https://github.com/seolcu/mini-kvm"
license: "MIT"
applies_to:
  host: "x86_64 Linux with KVM enabled and access to /dev/kvm"
  build: "gcc, make, binutils"
keywords:
  - "minimal KVM hypervisor C"
  - "KVM API example"
  - "debug triple fault kernel"
  - "hobby OS hypervisor"
---

## Scope

- **Is**: a KVM-based runner for kernels you wrote yourself, a diagnostic tool that explains guest failures, and a readable reference implementation of x86 virtualization.
- **Is not**: a production VMM (use QEMU, Firecracker or cloud-hypervisor), a cross-architecture emulator (x86 guests on x86 hosts only), or a sandbox.

Everything the README lists as working is covered by `make test`. Encouragement Award (Research), 2025-2 Ajou SoftCon.

```bash
git clone https://github.com/seolcu/mini-kvm.git && cd mini-kvm && make all
./kvm-vmm guest/hello
```
