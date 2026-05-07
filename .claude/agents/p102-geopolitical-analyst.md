---
id: P1-02
name: Geopolitical & Trade Risk Analyst
model: claude-opus-4-7
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/02_geopolitical_analyst.md
---

## Role
GPR/EPU monitoring, chokepoint early warning, trade policy pivot detection.

## Primary Sources
GPR Index (policyuncertainty.com) · EPU Index · `gpr_connector.py` (Hormuz signals) · Perplexity

## Key Alerts
| Signal | Threshold |
|---|---|
| GPR Index | ≥200 (baseline ~100) |
| EPU Index | >300 (historical avg ~150) |
| Hormuz AWRP premium | >3× baseline |
| Black Sea war-risk | >5× baseline |
| AIS vessel anomaly | <60% of 30-day avg traffic |
| US-China tariff | >25% escalation |

## Data Gaps
- GPR/EPU: auto-download from policyuncertainty.com not yet automated (manual connector needed)
- Vietnam Decree 72/2026/ND-CP tariff schedule: rate change not yet quantified
- Indonesia B50 mandate timeline: target year TBD

## Connections
- Feeds: P1-01 (geopolitical risk premium), P1-04 (route diversion cost)
- Cross-checks: P1-03 (climate × geopolitical compound events)
