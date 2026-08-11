# USDA FAS GATS — 미국 수출 통계

USDA FAS GATS(Global Agricultural Trade System) 기반 미국 농산물 수출 데이터.

## 폴더 구조 (2026-08 최신)

| 폴더 | 내용 | 코드 체계 | 단위 |
|---|---|---|---|
| `Oilseeds/Soybean Oil/Exports & Re-Exports/1507.10.0000/` | 조대두유 수출량·재수출량 | **HTS** | 물량 |
| `Oilseeds/Soybean Oil/Exports & Re-Exports/1507.90/.4020/` | 1회 정제 대두유 | **HTS** | 물량 |
| `Oilseeds/Soybean Oil/Exports & Re-Exports/1507.90/.4050/` | 완전 정제 대두유(기타) | **HTS** | 물량 |
| `Oilseeds/Soybean Oil/Exports & Re-Exports/1517.90.4035/` | 완전 경화 식용 대두유 | **HTS** | 물량 |
| `1507.10/` · `1507.90/` (구 구조) | 초기 수집분 | HS | 물량 |
| `export_value_top10/` | 9개년 수출액 상위 10개국 | HS 1201·2304·1507 | USD |

> ⚠️ **코드 체계 주의(조정자 확인)**: `Exports & Re-Exports` 하위는 표준 HS가 아닌
> **미국 관세율표(HTS, Harmonized Tariff Schedule of the United States)** 코드다.
> | HTS | 정의 |
> |---|---|
> | 1507.90.4020 | 1회 정제 대두유 — 정제했으나 **탈색·탈취 미실시** |
> | 1507.90.4050 | 대두유·분획물, **완전 정제**(수세·탈색·탈취) 화학적 미변성, 기타 |
> | 1517.90.4035 | 대두유, **완전 경화(hydrogenated)** 식용, 기타 |

## 재수출 결측 연도 (검증 대상 — C-02)
| HTS | 결측 연도 |
|---|---|
| 1507.10.0000 | 2010, 2016, 2018 |
| 1507.90.4020 | 2012~2014, 2020~2021 |
| 1517.90.4035 | 2010, 2020, 2026 |

→ 검증 스크립트: `scripts/verify_gats_reexport_gaps.py` (0 vs 미보고 판별)

- 파서: `scripts/ingest_gats_data.py`
