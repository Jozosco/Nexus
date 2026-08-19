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
NOAA CPC ONI(4열 ANOM — A-179) · `climate_connector.py` (Open-Meteo ERA5-Land 12개 산지 — A-026·A-110) · NASA POWER · USDM 가뭄(commodity_connector) · USDA WASDE

## Key Alerts
| Region | Threshold |
|---|---|
| US Iowa | 30-day precip deficit >40% below 30-yr normal |
| BR Mato Grosso | Max temp >38°C for 5+ consecutive days |
| AR Córdoba | Soil moisture <25th percentile |
| Any origin | SPI <−1.5 for 60 days → drought advisory |
| Pollination window | Forecast >+2°C anomaly (Jul–Aug US; Jan–Feb BR/AR) |

## Data Gaps (2026-08-19 갱신)
- 해소: USDM D0–D4 → drought.gov API 연동(commodity_connector) · ERA5 → Open-Meteo ERA5-Land 12개 산지(CDS 미사용 확정 — A-100), hourly 토양수분 일평균 복구(A-110)
- 잔존: SPI 미산출 · 위성 식생지수 미통합

## Connections
- Feeds: P1-01 (supply risk adjustment), P1-04 (harvest delay → CFR lead time)
- Cross-checks: P1-02 (climate × geopolitical compound events)
- Triggers: `SBO_CLIMATE_PRESSURE` 복합 지수는 **미구현 설계** — G1 일별 경보판(D-043)의
  현행 기후 트리거는 ENSO_ONI(±0.5)뿐. 경보판 등재는 지수 산출 구현 후.
  (구 'C-04 Slack webhook'은 폐기 **결정**됨 — C-007. 단 skill 파일에 지시 잔재 — 정합 스윕 대기)
