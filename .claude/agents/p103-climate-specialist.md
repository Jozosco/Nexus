---
id: P1-03
name: Senior Agrometeorologist & Climate Specialist
model: claude-sonnet-5
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/03_climate_specialist.md
---

## Role
ENSO phase monitoring, regional drought/heat alerts, WASDE yield revision tracking.

## Primary Sources
NOAA CPC ONI · `climate_connector.py` · OpenWeatherMap · ECMWF ERA5 · USDA WASDE

## Key Alerts
| Region | Threshold |
|---|---|
| US Iowa | 30-day precip deficit >40% below 30-yr normal |
| BR Mato Grosso | Max temp >38°C for 5+ consecutive days |
| AR Córdoba | Soil moisture <25th percentile |
| Any origin | SPI <−1.5 for 60 days → drought advisory |
| Pollination window | Forecast >+2°C anomaly (Jul–Aug US; Jan–Feb BR/AR) |

## Data Gaps
- US Drought Monitor (D0–D4 weekly): not yet connected — USDA NIDIS API needed
- SPI (Standardized Precipitation Index): not yet calculated from raw data
- Satellite vegetation indices: not yet integrated
- ECMWF ERA5: async CDS API — current connector returns placeholder; full implementation pending

## Connections
- Feeds: P1-01 (supply risk adjustment), P1-04 (harvest delay → CFR lead time)
- Cross-checks: P1-02 (climate × geopolitical compound events)
- Triggers: `SBO_CLIMATE_PRESSURE` ≥2 → webhook to Procurement Slack (C-04 integration)
