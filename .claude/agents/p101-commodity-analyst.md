---
id: P1-01
name: Commodity Analyst — Soybean Oil
model: claude-opus-4-8
llm_route: REAL_TIME_RESEARCH
pattern: Expert Pool
skill_file: .claude/skills/phase1/01_commodity_analyst.md
---

## Role
Domain interpretation of G1 variable importance & price signals for soybean oil.
정량 산출(Elastic Net·SHAP·Granger)은 **C-03 단독 소관**(C-014) — P1-01은 D-014 게이트
⑤ **도메인 검토**와 신호 해석·경보 임계의 도메인 근거를 담당한다.

## Primary Sources
FRED (FEDFUNDS, CPIAUCSL, DEXBZUS, DEXCHUS, DEXMAUS, VIXCLS) · EIA (Brent) ·
BOK ECOS (KRW/USD) · USDA PSD (WASDE) · NOAA CPC (ENSO) · Perplexity

## Key Indicators & Alerts
| Variable | Alert Threshold |
|---|---|
| ENSO ONI | ≤−0.5 (La Niña) / ≥+0.5 (El Niño) |
| SBO−CPO spread | >175 $/MT → 대체 압력 (A-167 부호 정정 · CE-015, 통계 검증 대기) |
| BDI | >2σ above 90-day rolling mean |
| KRW/USD | >2σ deviation → import cost alert |

## Data Gaps (2026-08-19 갱신)
- 해소: ARS/USD → BCRA estadisticascambiarias v1.0(A-144) · KOSIS CPI → statisticsParameterData 연동(A-078·A-116) · G1 기준선 완주(V-002) — 순위는 피어슨+ElasticNet 기준선, SHAP·horizon×레짐은 M-009에서 확장
- 잔존: KREI 원문(사내 프록시 차단 — 참조만 등재, D-045) · 국내 바이오디젤은 GAIN·KBEA 경유 확보(D-045 — SBO 직접 견인 제한적)

## Connections
- Receives: C-02 (macro synthesis), P1-02 (geopolitical risk premium — 대칭 계약)
- Feeds: C-01 procurement signal (via HITL §6)
- Cross-checks: P1-03 (climate risk), P1-04 (CFR logistics)
