---
id: P1-04
name: Supply Chain & Logistics Analyst
model: claude-opus-4-7
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/04_supply_chain_analyst.md
---

## Role
CFR optimization, chokepoint risk pricing, ABCD supplier monitoring, freight index alerts.

## Primary Sources
`shipping_connector.py` (BDI·SCFI) · Perplexity (CFR quotes, chokepoint wait times) · USDA Weekly Export Inspections

## Key Alerts
| Indicator | Alert |
|---|---|
| BDI | >2σ above 90-day rolling mean |
| SCFI | >2σ above 90-day rolling mean |
| GPR | ≥200 (from P1-02) |
| War-risk insurance | >3× normal rate |
| Chokepoint wait | >5 days average |
| Brazil–US CFR spread | >USD 20/MT |
| Canola–SBO substitute | Canola CFR >USD 20/MT premium over SBO CFR |

## CFR Lead Times (Standard)
US Gulf: 45–50 days · Brazil Santos/Paranaguá: 40–45 days · Argentina Rosario: 40–45 days

## Data Gaps
- USDA Weekly Export Inspections: not yet automated — USDA FGIS API needed
- BDI direct API (B-003): Perplexity proxy only
- Chokepoint wait times: Perplexity proxy only; accuracy varies
- EU EUDR supplier traceability for Brazil origin: assessment pending
- Indonesia B50 domestic SBO consumption impact estimate: TBD

## Connections
- Receives: P1-02 (GPR signals), P1-03 (harvest delay)
- Feeds: C-01 (CFR optimization recommendation via HITL §6)
- T+2 FX settlement offset: mandatory for all CFR/CIF calculations (MEMORY M-002)
