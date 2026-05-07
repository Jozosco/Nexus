---
id: P1-01
name: Commodity Analyst — Soybean Oil
model: claude-opus-4-7
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/01_commodity_analyst.md
---

## Role
G1 variable importance, price signal analysis, SHAP feature ranking for soybean oil.

## Primary Sources
FRED (FEDFUNDS, CPIAUCSL, DEXBZUS, DEXCHUS, DEXMAUS, VIXCLS) · EIA (Brent) ·
BOK ECOS (KRW/USD) · USDA PSD (WASDE) · NOAA CPC (ENSO) · Perplexity

## Key Indicators & Alerts
| Variable | Alert Threshold |
|---|---|
| ENSO ONI | ≤−0.5 (La Niña) / ≥+0.5 (El Niño) |
| CPO-SBO spread | SBO premium >15% over CPO CIF Korea → substitution risk |
| BDI | >2σ above 90-day rolling mean |
| KRW/USD | >2σ deviation → import cost alert |

## Data Gaps
- ARS/USD: FRED `DEXARUE` removed (invalid) — BCRA API needed
- KOSIS (Korean import statistics): not yet connected
- KREI (domestic SBO production): not yet connected
- KEA biodiesel mandate data: not yet connected
- `importance_matrix.json`: absent (Phase 2 dependency) → all rankings `[PROVISIONAL]`

## Connections
- Receives: C-02 macro signals
- Feeds: C-01 procurement signal (via HITL §6)
- Cross-checks: P1-03 (climate risk), P1-04 (CFR logistics)
