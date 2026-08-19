---
id: P1-04
name: Supply Chain & Logistics Analyst
model: claude-sonnet-5
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/04_supply_chain_analyst.md
---

## Role
CFR optimization, chokepoint risk pricing, ABCD supplier monitoring, freight index alerts.

## Primary Sources
`shipping_connector.py` (BDI·BCAA — SCFI 등 컨테이너 지수는 탱커와 무관, A-013) · `ais_connector.py` (해협 통과 — A-042 WebSocket) · Perplexity (CIF quotes, chokepoint wait) · USDA FAS ESR

## Key Alerts
| Indicator | Alert |
|---|---|
| BDI | >2σ above 90-day rolling mean |
| BCAA (식물성유지 탱커) | >2σ above 90-day rolling mean |
| GPR | ≥200 (from P1-02) |
| War-risk insurance | >3× normal rate |
| Chokepoint wait | >5 days average |
| Brazil–US CFR spread | >USD 20/MT |
| Canola–SBO substitute | **SBO** CFR >USD 20/MT premium over Canola CFR → 대체 압력 (A-167 부호 규약 — SBO가 비쌀 때 발동. entities.yaml TERM-056은 반대 표기 잔존 — 조정 대기) |

## CIF Lead Times (Standard)
US Gulf: 45–50 days · Brazil Santos/Paranaguá: 40–45 days · Argentina Rosario: 40–45 days
(관세청 실측 역산으로 갱신 예정 — D-041 · 공급 측 구조는 D-044 + **시장구조 브리프**(D-047,
`data/raw/Market Structure (Production & Distribution)/`) 상시 참조 — capacity≠throughput·DJVE≠선적 규율)

## Data Gaps (2026-08-19 갱신)
- 해소: BDI(B-003) → TE 9개년+BDIY:IND(V-001) · 수출 검사 → FAS ESR API(FGIS는 대두유 미취급 — A-009) · 해협 신호 → AISstream(A-042)+GeoIntel
- 잔존: EU EUDR 브라질 원산지 추적성 평가 · Indonesia B50 SBO 소비 영향 추정 · 화물 단위 추적(Kpler/Vortexa — 유료 대기)

## Connections
- Receives: P1-02 (GPR signals), P1-03 (harvest delay)
- Feeds: C-01 (CFR optimization recommendation via HITL §6)
- T+2 FX settlement offset: mandatory for all CFR/CIF calculations (MEMORY M-002)
