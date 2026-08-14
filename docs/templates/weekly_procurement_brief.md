# 주간 조달 브리프 — {YYYY-MM-DD} (W{주차})

> G2 운영 현실화 계층(D-041) 산출 템플릿. 원천 보고서 2종을 실무자 소비 형태로 결합함.
> 원천: `reports/market/landed_cost_band_{date}.md` · `reports/market/procurement_alternatives_{date}.md`
> 생성: `python -m src.forecasting.landed_cost` → `python -m src.forecasting.procurement_alternatives`
> 배포 채널: 일별 비정형 다이제스트와 동일(Actions Step Summary + 아티팩트 — A-163).

---

## 1. 도착가 밴드 (CFR 한국항, 조대두유, USD/MT)

| 분위 | 도착가 밴드 | CBOT 층 | 내재 basis+운임층 |
|---|---|---|---|
| P10 | {band_p10} | {cbot_p10} | {basis_lo} |
| P50 | **{band_p50}** | {cbot_p50} | {basis_mid} |
| P90 | {band_p90} | {cbot_p90} | {basis_hi} |

- 운임 레짐: **{평시|경계|급등}** (BDI 90일 z = {z}) — 시나리오 분위 적용 상태
- 전주 대비: P50 {±Δ} $/MT · 밴드폭 {±Δ} $/MT
- 국가별 실측 CIF 최근월: {국가: 값} (벌크 ≥100 MT 기준)

## 2. 4축 대안 (참고 정보 — 지시 아님)

| 축 | 이번 주 신호 | 정량 델타 ($/MT) | 참고 방향 |
|---|---|---|---|
| ①시점 (지금 vs 2·4주 대기) | {밴드 비대칭 ±Δ} | 상방 {+Δ} vs 하방 {−Δ} | {대기/확정 우호 신호} |
| ②커버리지 (선매입 개월) | 레짐 {평시\|경계\|급등} → 권장 {n~m}개월 | 1개월 연장 = {P50} 선확정 | {유지/연장 검토} |
| ③Incoterms (CFR vs FOB) | BDI z = {z} (§3d 임계 1/2) | 운임 프리미엄 근사 {+Δ} | {§3d 분기 결과} |
| ④대체유지 (팜·유채·해바라기) | z격차 {값} · 스프레드 {값\|환산 대기} | 임계 CPO−SBO $175(CE-015) | {전환 검토/해당 없음} |

## 3. 인과 근거 (ontology causal_edges — validated 우선 인용)

- {CE-ID} {체인 요약 한 줄} — 이번 주 관련 관측: {지표 현황}
- {CE-ID} … (2~4건. candidate 엣지 인용 시 "검증 대기" 병기 의무 — S-1)
- 교란 전파 참조: `src/semantic/ontology.yaml` supply_chain.routes (RT-USG-KR·RT-SANTOS-KR·RT-ROSARIO-KR,
  리드타임 40~50일 — 관세청 실측 역산 갱신 예정)

## 4. 신선도·한계

- CBOT 층: 마지막 관측 {date} (경과 {n}일) · 원천 {정산가|UTC 진단 계열}
- 관세청 실측 CIF: 마지막 월 {YYYY-MM} (월간 확정치 — 익월 15일경 공표)
- BDI: 마지막 관측 {date} · BCAA 실측은 §5 유료 승인 전 프록시 상태
- CBOT 층은 G2 분위수 모델 산출 전 **임시 스탠드인**(60거래일 경험 분포)
- {이번 주 데이터 갭·수집 실패가 있으면 명시 — 없으면 "특이사항 없음"}

## 5. ⚠️ HITL 고지 (필수 — 삭제 금지)

**본 브리프는 Buy/Hold 지시가 아님.** 모든 수치는 조건별 기대비용 차이의 참고 정보이며,
실제 조달 의사결정은 **CLAUDE.md §6 HITL 게이트**(Explore→Plan→Validate→Execute, 인간 승인
필수)를 통과해야 함. AI는 권고만 하고 실행하지 않음(§1 Decision output — Human gate).
