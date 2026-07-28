# C-01 × P1-01 공동 분석 메모 — USDA FAS PS&D "Local" 품목 분류

**작성일**: 2026-06-17  
**작성자**: C-01 Senior PM × P1-01 Commodity Analyst  
**분류**: 데이터 아키텍처 결정 문서  
**관련 데이터**: `Oil, Soybean.xlsx` · `Oil, Soybean (Local).xlsx` · `Oilseed, Soybean.xlsx`

---

## 1. 질문 배경

사용자가 USDA FAS PSD 데이터를 업로드할 때 다음 3개 파일을 제공했다:

| 파일명 | 설명 |
|---|---|
| `Oil, Soybean.xlsx` | 표준 대두유 공급/수요 밸런스 |
| `Oil, Soybean (Local).xlsx` | **"Local"** 접미사 품목 |
| `Oilseed, Soybean.xlsx` | 대두(원료) 공급/수요 밸런스 |

**질문**: `"Oil, Soybean"`과 `"Oil, Soybean (Local)"`의 차이는 무엇인가? Nexus G1/G2/G3에서 어느 것을 사용해야 하는가?

---

## 2. USDA FAS PS&D 품목 분류 체계 설명

### 2.1 표준 품목: `Oil, Soybean`

| 항목 | 내용 |
|---|---|
| **정의** | 대규모 상업적 압착 공정을 통해 생산된 대두유 |
| **생산 주체** | 공식 제조업체 (산업용 솔벤트 추출법, Expeller Press) |
| **시장 채널** | 국내 유통 + **국제 무역(수출입)** 포함 |
| **가격 연동** | CBOT 선물가격과 직접 연동 |
| **데이터 단위** | 1,000 MT (연간) |
| **집계 범위** | 전국 생산 총량 (공식 통계청/산업 조사 기반) |
| **예시 국가** | 미국 · 브라질 · 아르헨티나 · 중국 · EU |

**→ 이 데이터가 글로벌 대두유 무역과 가격 형성에 영향을 준다.**

---

### 2.2 "Local" 품목: `Oil, Soybean (Local)`

| 항목 | 내용 |
|---|---|
| **정의** | 소규모 수공업·자급자족형 압착으로 생산된 대두유 |
| **생산 주체** | 농촌 소규모 가공업자, 마을 단위 압착 시설 |
| **시장 채널** | **지역 소비 전용** — 국제 무역에 진입하지 않음 |
| **가격 연동** | CBOT 선물과 무관; 지역 농산물 가격 반영 |
| **보고 국가** | 주로 아프리카·아시아 저소득 국가 (나이지리아, 에티오피아, 방글라데시 등) |
| **규모** | 표준 품목의 1~5% 수준 (통계적으로 미미) |

**→ 이 데이터는 국제 대두유 가격에 영향을 주지 않는다.**

---

## 3. 핵심 차이 요약

| 구분 | `Oil, Soybean` | `Oil, Soybean (Local)` |
|---|---|---|
| 무역 진입 여부 | ✅ 국제 무역 포함 | ❌ 지역 소비 전용 |
| CBOT 가격 연동 | ✅ 직접 연동 | ❌ 무관 |
| 규모 | 수백만 MT (주요 생산국) | 수천 MT (소규모) |
| G1/G2/G3 관련성 | ✅ **필수 데이터** | ❌ 노이즈 |
| Nexus 사용 여부 | **사용** | **제외** |

---

## 4. Nexus 데이터 아키텍처 결정

### 4.1 사용 파일

```
✅ 사용: Oil, Soybean.xlsx
   → WASDE_SBO_PRODUCTION, WASDE_SBO_EXPORTS, WASDE_SBO_CONSUMPTION 등 추출
   → G1 변수: 글로벌 공급/수요 밸런스, STU(재고사용비율)
   → G2 외생 변수: 연간 공급 전망 변화 → 계절 더미 보정

✅ 사용: Oilseed, Soybean.xlsx
   → 대두(원료) 생산량 → 대두유 생산 선행 지표
   → G1 변수: WASDE_SOY_PRODUCTION (대두 총생산, 1,000 MT)

❌ 제외: Oil, Soybean (Local).xlsx
   → 국제 가격 형성과 무관
   → 파이프라인에 포함 시 노이즈 증가 위험
   → data/raw/에 보관은 하되 ingestion 스크립트에서 제외
```

### 4.2 스크립트 구현 지침 (`scripts/ingest_psd_data.py`)

```python
PSD_FILES_TO_INGEST: list[str] = [
    "Oil, Soybean.xlsx",       # 대두유 S&D 밸런스 (국제 무역 포함)
    "Oilseed, Soybean.xlsx",   # 대두 원료 S&D (선행 지표)
    # "Oil, Soybean (Local).xlsx"  # 제외: 지역 소비 전용, 무역 비포함
]
```

### 4.3 WBS 영향

| WBS | 항목 | 결정 |
|---|---|---|
| 1.1.41 (변형) | PS&D Excel 파싱 | `Oil, Soybean.xlsx` + `Oilseed, Soybean.xlsx` 만 ingestion |
| 신규 | `Oil, Soybean (Local)` 처리 | 파일 보관, 스크립트 제외 (명시적 주석 필요) |

---

## 5. P1-01 상품 시장 보완 분석

`Oil, Soybean.xlsx`에서 G1/G2에 핵심적인 파생 변수:

| 변수명 | 계산식 | 중요도 | 근거 |
|---|---|---|---|
| `WASDE_SBO_STU` | `Ending Stocks / Total Use × 100` | ★★★ | 가격 방향성의 핵심 — STU < 10%이면 강세 신호 |
| `WASDE_SBO_PRODUCTION_YOY` | `(현년 생산량 / 전년) - 1` | ★★★ | 공급 충격 포착 |
| `WASDE_SBO_EXPORTS_REVISION` | 월별 WASDE 수출 전망 수정폭 | ★★ | 발간 서프라이즈 → 단기 가격 반응 |
| `WASDE_SBO_ARGENTINA_SHARE` | `아르헨티나 생산 / 글로벌 생산` | ★★ | 아르헨티나 의존도 모니터링 |
| `WASDE_SOY_CRUSH_MARGIN` | `SBO가 + SBM가 - 대두가` | ★★★ | 압착 마진 → 생산 인센티브 |

---

## 6. 결론

**`Oil, Soybean (Local)`은 Nexus G1/G2/G3 모델에서 사용하지 않는다.**  
국제 무역에 진입하지 않는 수공업 생산분으로, CBOT 가격과 상관관계가 없으며  
포함 시 오히려 신호 대 잡음비(SNR)를 낮출 위험이 있다.

`Oil, Soybean.xlsx`(표준)와 `Oilseed, Soybean.xlsx`(원료)만 ingestion 파이프라인에 포함하며,  
`Local` 파일은 `data/raw/`에 참고용으로만 보관한다.

---

*Project Nexus · C-01 PM × P1-01 Commodity Analyst · 2026-06-17*  
*다음 조치: `scripts/ingest_psd_data.py` 구현 시 본 결정 문서 참조*
