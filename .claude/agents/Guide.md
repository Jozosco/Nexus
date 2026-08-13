# Project Agent Guide

This directory contains role contracts. Agent files define responsibility and hand-off boundaries; they do
not override `CLAUDE.md`, `AGENTS.md`, or path-scoped rules.

## Coordination Order

For milestone, infrastructure, data migration, or pipeline reliability work:

1. **C-04 leads the technical audit and implementation design** for ingestion, document processing,
   GitHub Actions, Azure ML, and data hand-offs.
2. **C-01 validates scope, sequencing, WBS status, blockers, and HITL gates**.
3. C-04 supplies evidence by repository path, symbol/job name, observed behavior, and a minimal safe fix.
4. C-01 returns `task_id | description | status | blocker` and does not infer missing information.
5. The implementing agent converts agreed P0/P1 items into a branch, synthetic tests, and a draft PR.

## Required Review Questions

| Area | C-04 evidence | C-01 decision |
|---|---|---|
| Target data | time basis, unit, session calendar, coverage, provenance | model entry allowed/blocked |
| Workflow | dependency graph, exit code, artifact existence, permissions | milestone gate and priority |
| Feature mart | as-of alignment, unit identity, revision contamination | usable scope and exceptions |
| G1/G2 | actual executable code, temporal CV, baseline/evaluation evidence | completion claim allowed/blocked |
| Migration | manifest, checksum, success marker, identity/RBAC boundary | rollout stage and hand-off readiness |

## Confidentiality

Repository outputs may contain only generalized environment-variable names and public project facts. Keep
account names, subscription/resource identifiers, network topology, company-internal system mappings,
credentials, and personal availability outside the repository in an approved private hand-off channel.

## Completion Evidence

A milestone is complete only when its required inputs pass fail-closed gates and a clean environment can
reproduce the artifact. Documentation-only method names, skipped tests, warning-only failures, or a report
generated with a fallback target do not count as implementation evidence.
