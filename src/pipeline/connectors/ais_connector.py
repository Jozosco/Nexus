"""
AIS 선박 추적 커넥터 — WBS 1.1.6 확장 (지정학 리스크 카테고리)
수집 대상: 주요 해협(호르무즈·말라카·파나마) 통과 탱커 수 및 위험 신호

데이터 소스: AISstream.io WebSocket API (Hormuz Monitor 참조 아키텍처)
  - 호르무즈 해협 좌표: 25.75-27.1°N, 55.75-57.45°E
  - 말라카 해협 좌표: 1.1-3.0°N, 100.5-104.0°E
  - 파나마 운하 좌표: 7.7-9.5°N, 79.5-80.1°W

대두유 관련성:
  - 호르무즈 봉쇄 → 유가 급등 → 벙커유 비용 → CFR 운임 프리미엄 +3~8%
  - 말라카 해협 → 브라질/아르헨티나산 대두유 → 중국/인도 주요 통로
  - 파나마 운하 → 미국산 대두유 → 아시아 수출 경로

현행 구현 (Phase A):
  - AISstream.io REST API (WebSocket 대신 HTTP 폴링 방식)
  - 환경변수: AISSTREAM_API_KEY (aisstream.io 무료 가입 후 발급)
  - 폴백: Perplexity 실시간 검색 (API 키 미등록 시)

Phase B 계획:
  - AISstream.io WebSocket 실시간 연결 (hormuzmoni 패턴 참조)
  - MarineTraffic API v3 (유료, 더 정확한 선박 분류)
  - PortWatch (세계은행 공개 API) — 항구별 입출항 통계

C-01 × P-02 결정 (2026-05-26):
  - AISstream.io Phase A 수용 (무료 tier, 좌표 기반 필터)
  - MarineTraffic Phase B 검토 (정확도 향상 vs. 비용 트레이드오프)
  - 수집 지표: 탱커 통과 수, 방향(인바운드/아웃바운드), 위험 레벨

참조: github.com/rahoney/hormuz-monitor (AISstream 아키텍처)

실행 환경: GitHub Actions (스케줄: 1.1.6 지정학 리스크 커넥터와 동일 실행)
"""

from __future__ import annotations

import os
import re
from datetime import date
from typing import Any

import pandas as pd

OUTPUT_DIR = "data/raw"

# 주요 해협 좌표 (Hormuz Monitor 참조)
STRAITS: dict[str, dict[str, Any]] = {
    "HORMUZ": {
        "name_ko": "호르무즈 해협",
        "bbox": {"min_lat": 25.75, "max_lat": 27.1, "min_lon": 55.75, "max_lon": 57.45},
        "sbo_relevance": "유가 충격 → 벙커유 비용 → CFR 운임 +3~8%",
    },
    "MALACCA": {
        "name_ko": "말라카 해협",
        "bbox": {"min_lat": 1.1, "max_lat": 3.0, "min_lon": 100.5, "max_lon": 104.0},
        "sbo_relevance": "브라질/아르헨티나 → 중국/인도 주요 통로",
    },
    "PANAMA": {
        "name_ko": "파나마 운하",
        "bbox": {"min_lat": 7.7, "max_lat": 9.5, "min_lon": -80.1, "max_lon": -79.5},
        "sbo_relevance": "미국산 대두유 → 아시아 수출 경로",
    },
}

# AIS 선박 유형 (탱커: type 80-89, 화학/유류 탱커: 80, 82, 83, 84, 85)
TANKER_TYPE_CODES = {80, 81, 82, 83, 84, 85, 86, 87, 88, 89}


def _fetch_strait_via_perplexity(strait_key: str) -> list[dict]:
    """Perplexity 실시간 검색으로 해협 탱커 통과 상황 수집 (AISstream 미등록 시 폴백)."""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        return []

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        strait = STRAITS[strait_key]
        prompt = (
            f"What is the current tanker traffic status at the {strait_key.replace('_', ' ').title()}? "
            "Provide: (1) number of tankers transiting today or this week, "
            "(2) any disruptions, blockages, or unusual incidents in past 7 days, "
            "(3) overall transit risk level: HIGH / MEDIUM / LOW. "
            "Format: TRANSITS: [number] | DISRUPTION: [yes/no + brief] | RISK: [HIGH/MEDIUM/LOW] | SOURCE: [source]"
        )
        r = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}],
        )
        text = r.choices[0].message.content
        today = date.today().isoformat()
        rows = []

        transit_match = re.search(r"TRANSITS:\s*(\d+)", text, re.IGNORECASE)
        if transit_match:
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/AIS",
                "indicator_code": f"AIS_{strait_key}_TANKER_COUNT",
                "value":          float(transit_match.group(1)),
                "unit":           "vessels/day",
                "note":           f"[PERPLEXITY-PROXY: {strait['name_ko']} 탱커 통과 수]",
            })

        risk_match = re.search(r"RISK:\s*(HIGH|MEDIUM|LOW)", text, re.IGNORECASE)
        if risk_match:
            level_map = {"HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}
            level = risk_match.group(1).upper()
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/AIS",
                "indicator_code": f"AIS_{strait_key}_RISK",
                "value":          level_map[level],
                "unit":           "1=Low/2=Med/3=High",
                "note":           f"[QUALITATIVE:{level}] {strait['name_ko']} 통과 위험",
            })
        return rows
    except Exception as e:
        print(f"[경고] Perplexity {strait_key} AIS 폴백 실패: {e}")
        return []


def _fetch_strait_via_aisstream(strait_key: str, api_key: str) -> list[dict]:
    """AISstream.io WebSocket API로 해협 탱커 통과 수 수집.

    ※ AISstream.io는 WebSocket 전용 API입니다 (REST 엔드포인트 없음).
       WebSocket 주소: wss://stream.aisstream.io/v0/stream
       인증: 연결 직후 JSON payload에 APIkey 필드 전송
       참조: github.com/Hue-Jhan/OSINT-War-Room, github.com/JJ/AISstreamer

    Phase A GitHub Actions 환경에서는 websocket-client 패키지로 동기적으로 수집.
    Phase B에서 asyncio + websockets 비동기 스트리밍으로 전환 예정.

    유의사항:
      - 무료 tier에서 과도한 연결 시 IP 차단 발생 가능 (24시간 대기 또는 키 재발급)
      - AISstream.io는 "experimental" 서비스로 엔드포인트 변경 가능성 있음
    """
    today = date.today().isoformat()
    strait = STRAITS[strait_key]
    bbox   = strait["bbox"]

    try:
        import websocket  # pip install websocket-client
        import json as _json

        ws_url    = "wss://stream.aisstream.io/v0/stream"
        subscribe = _json.dumps({
            "APIkey":       api_key,
            "BoundingBoxes": [[
                [bbox["min_lat"], bbox["min_lon"]],
                [bbox["max_lat"], bbox["max_lon"]],
            ]],
            "FilterMessageTypes": ["PositionReport", "ShipStaticData"],
        })

        ships_seen: dict[str, dict] = {}
        MAX_MESSAGES = 200

        def _on_message(ws_obj, message):
            try:
                data = _json.loads(message)
                mmsi = str(data.get("MetaData", {}).get("MMSI", ""))
                ship_type = data.get("Message", {}).get("ShipStaticData", {}).get("Type", 0)
                if mmsi:
                    ships_seen[mmsi] = {"shipType": ship_type}
                if len(ships_seen) >= MAX_MESSAGES:
                    ws_obj.close()
            except Exception:
                pass

        def _on_open(ws_obj):
            ws_obj.send(subscribe)

        ws = websocket.WebSocketApp(ws_url, on_message=_on_message, on_open=_on_open)
        ws.run_forever(ping_interval=20, ping_timeout=10)

        tankers = [
            s for s in ships_seen.values()
            if s.get("shipType", 0) in TANKER_TYPE_CODES
        ]

        rows = [{
            "price_date":     today,
            "source_name":    "AISstream/WebSocket",
            "indicator_code": f"AIS_{strait_key}_TANKER_COUNT",
            "value":          float(len(tankers)),
            "unit":           "vessels",
            "note":           (
                f"[AIS-OFFICIAL: {strait['name_ko']} 탱커 수 "
                f"({len(ships_seen)}척 관측 중 탱커 {len(tankers)}척)]"
            ),
        }]
        print(f"[완료] AIS {strait_key}: {len(ships_seen)}척 관측, 탱커 {len(tankers)}척")
        return rows

    except ImportError:
        print(f"[경고] websocket-client 미설치 — AISstream WebSocket 수집 건너뜀. Perplexity 폴백 사용.")
        return []
    except Exception as e:
        print(f"[경고] AISstream {strait_key} WebSocket 수집 실패: {e}")
        return []


def _compute_risk_composite(rows: list[dict]) -> list[dict]:
    """수집된 AIS 데이터로 SBO 공급 위험 복합 지수 계산.

    호르무즈 모니터 참조: Vessel_Score(40%) + Geo_Score(30%) + Brent_Score(20%) + VIX_Score(10%)
    Nexus 적용: AIS_HORMUZ(50%) + AIS_MALACCA(30%) + AIS_PANAMA(20%)
    탱커 수 감소 → 위험 상승 (역 관계)
    """
    if not rows:
        return []

    today = date.today().isoformat()
    counts = {
        "HORMUZ":  next((r["value"] for r in rows if "HORMUZ_TANKER_COUNT" in r["indicator_code"]), None),
        "MALACCA": next((r["value"] for r in rows if "MALACCA_TANKER_COUNT" in r["indicator_code"]), None),
        "PANAMA":  next((r["value"] for r in rows if "PANAMA_TANKER_COUNT" in r["indicator_code"]), None),
    }

    # 각 해협 정상 기준: Hormuz ~35척/일, Malacca ~80척/일, Panama ~35척/일 (업계 평균)
    NORMAL_COUNTS = {"HORMUZ": 35.0, "MALACCA": 80.0, "PANAMA": 35.0}
    WEIGHTS = {"HORMUZ": 0.50, "MALACCA": 0.30, "PANAMA": 0.20}

    composite = 0.0
    valid_weight = 0.0
    for strait, count in counts.items():
        if count is not None and NORMAL_COUNTS[strait] > 0:
            # 정상 대비 비율: 낮을수록 위험. 0.5 이하 → 최대 위험 (100점)
            ratio = count / NORMAL_COUNTS[strait]
            score = max(0.0, min(100.0, (1.0 - ratio) * 100))
            composite += score * WEIGHTS[strait]
            valid_weight += WEIGHTS[strait]

    if valid_weight > 0:
        composite /= valid_weight  # 가중 평균 정규화
        return [{
            "price_date":     today,
            "source_name":    "AIS/NexusComposite",
            "indicator_code": "SBO_STRAIT_RISK_COMPOSITE",
            "value":          round(composite, 1),
            "unit":           "0-100 (높을수록 공급 위험)",
            "note":           f"[COMPOSITE: Hormuz 50%+Malacca 30%+Panama 20% | 수집값: {counts}]",
        }]
    return []


def run() -> None:
    """AIS 탱커 데이터 수집 및 대두유 공급 위험 지수 산출."""
    import time as _time
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    # BACKFILL_MODE: AIS는 실시간 데이터 → 백필 불가 (건너뜀)
    if os.environ.get("BACKFILL_MODE", "").lower() == "true":
        print("[정보] BACKFILL_MODE 활성화 — AIS 실시간 수집 건너뜀 (역사 데이터 없음)")
        return

    ais_key = os.environ.get("AISSTREAM_API_KEY", "").strip()
    all_rows: list[dict] = []

    for strait_key in STRAITS:
        if ais_key:
            rows = _fetch_strait_via_aisstream(strait_key, ais_key)
        else:
            print(f"[정보] AISSTREAM_API_KEY 미등록 — {strait_key} Perplexity 폴백")
            rows = _fetch_strait_via_perplexity(strait_key)
        all_rows.extend(rows)
        _time.sleep(0.5)  # 레이트 리밋

    # 복합 위험 지수 산출
    composite = _compute_risk_composite(all_rows)
    all_rows.extend(composite)

    if not all_rows:
        print("[경고] AIS 데이터: 수집된 항목 없음 — AISSTREAM_API_KEY 또는 PERPLEXITY_API_KEY 확인")
        return

    df = pd.DataFrame(all_rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    out = f"{OUTPUT_DIR}/ais_strait_risk_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] AIS 해협 탱커 데이터 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
