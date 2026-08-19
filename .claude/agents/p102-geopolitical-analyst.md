---
id: P1-02
name: Geopolitical & Trade Risk Analyst
model: claude-opus-4-8
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/02_geopolitical_analyst.md
---

## Role
GPR/EPU monitoring, chokepoint early warning, trade policy pivot detection.

## Primary Sources
GPR Index (matteoiacoviello.com — A-138 이관) · EPU Index · `gpr_connector.py` (Hormuz·정책뉴스 프록시) · `geointel_connector.py` · Perplexity

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
- (해소) GPR 자동수집: matteoiacoviello.com 체인+xlrd로 연동 완료 (A-138·A-147)
- EPU Index: **수집 경로 미구현** — Perplexity 임시 질의만 가능(임계 >300은 수집 구현 전까지 참조용)
- Vietnam Decree 72/2026/ND-CP tariff schedule: rate change not yet quantified
- Indonesia B50 mandate timeline: target year TBD

## Connections
- Feeds: P1-01 (geopolitical risk premium), P1-04 (route diversion cost)
- Cross-checks: P1-03 (climate × geopolitical compound events)
