#!/usr/bin/env python3
"""
한국 공공기관 API 호스트 연결 진단 (A-095)

배경: KOSIS·관세청에서 `httpx.ConnectTimeout: timed out`이 반복 발생. IPv4 강제(A-085)로도
해소되지 않아, **어느 계층에서 실패하는지**를 분리 측정해야 원인을 특정할 수 있다.
httpx의 ConnectTimeout은 DNS 해석·TCP 핸드셰이크·TLS 협상을 모두 뭉뚱그리므로 단계를 쪼갠다.

측정 단계:
  ① DNS  — getaddrinfo로 A/AAAA 레코드 해석 (실패 시 DNS 문제)
  ② TCP  — 해석된 IP마다 직접 socket.connect (실패 시 방화벽·경로·차단)
  ③ TLS  — HTTPS 포트 핸드셰이크 (실패 시 SNI·인증서 경로)
  ④ HTTP — 실제 GET (http/https 양쪽, 상태코드·소요시간)

판정에 쓰는 신호:
  - DNS 성공 + TCP 전 IP 실패 → 호스트/네트워크 경로 차단(레이트리밋 IP 밴 포함 가능)
  - TCP 성공 + HTTP 타임아웃   → 애플리케이션 계층 지연(서버 과부하)
  - http 실패 + https 성공     → 평문 80 포트 경로 문제 → 스킴 전환으로 우회 가능

의존성: httpx (표준 라이브러리 socket·ssl 사용)
실행: GitHub Actions (샌드박스 프록시는 해당 호스트 차단 — A-069)
"""
from __future__ import annotations

import os
import socket
import ssl
import time

import httpx

HOSTS: list[tuple[str, str]] = [
    ("apis.data.go.kr", "/1220000/nitemtrade/getNitemtradeList"),   # 관세청 GW
    ("kosis.kr",        "/openapi/Param/statisticsParameterData.do"),  # KOSIS
    ("ecos.bok.or.kr",  "/api/StatisticSearch"),                    # 한국은행 ECOS
]
CONNECT_TIMEOUT = 10.0
HTTP_TIMEOUT    = 20.0


def _resolve(host: str) -> list[str]:
    """A 레코드(IPv4) 해석. 실패 시 빈 리스트."""
    try:
        infos = socket.getaddrinfo(host, None, family=socket.AF_INET,
                                   type=socket.SOCK_STREAM)
        return sorted({i[4][0] for i in infos})
    except socket.gaierror as e:
        print(f"    ① DNS  ❌ 해석 실패: {e}")
        return []


def _tcp(ip: str, port: int) -> tuple[bool, float, str]:
    """단일 IP·포트 TCP 연결 시도 → (성공, 소요초, 사유)."""
    t0 = time.monotonic()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(CONNECT_TIMEOUT)
    try:
        s.connect((ip, port))
        return True, time.monotonic() - t0, ""
    except Exception as e:
        return False, time.monotonic() - t0, f"{type(e).__name__}: {e}"
    finally:
        s.close()


def _tls(host: str, ip: str) -> tuple[bool, str]:
    """SNI 기반 TLS 핸드셰이크 확인(443)."""
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((ip, 443), timeout=CONNECT_TIMEOUT) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                return True, tls.version() or "unknown"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _http(url: str, params: dict) -> str:
    """실제 GET — 상태코드와 소요시간 반환(본문은 기록하지 않음: 키 유출 방지)."""
    t0 = time.monotonic()
    try:
        transport = httpx.HTTPTransport(local_address="0.0.0.0", retries=1)
        with httpx.Client(transport=transport, timeout=HTTP_TIMEOUT) as c:
            r = c.get(url, params=params)
        return f"✅ HTTP {r.status_code} ({time.monotonic()-t0:.1f}s · {len(r.content):,}B)"
    except Exception as e:
        return f"❌ {type(e).__name__} ({time.monotonic()-t0:.1f}s): {str(e)[:60]}"


def diagnose(host: str, path: str) -> None:
    print(f"\n=== {host} ===")
    ips = _resolve(host)
    if not ips:
        return
    print(f"    ① DNS  ✅ {len(ips)}개 IPv4: {', '.join(ips)}")

    tcp_ok = []
    for ip in ips:
        for port in (80, 443):
            ok, secs, why = _tcp(ip, port)
            mark = "✅" if ok else "❌"
            print(f"    ② TCP  {mark} {ip}:{port} ({secs:.1f}s) {why}")
            if ok:
                tcp_ok.append((ip, port))

    if any(p == 443 for _, p in tcp_ok):
        ip = next(i for i, p in tcp_ok if p == 443)
        ok, info = _tls(host, ip)
        print(f"    ③ TLS  {'✅' if ok else '❌'} {ip}: {info}")

    # ④ 실제 요청 — 키가 필요한 호스트는 최소 파라미터만 전달
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    params: dict = {}
    if host == "apis.data.go.kr" and key:
        params = {"serviceKey": key, "strtYymm": "202601", "endYymm": "202601",
                  "hsSgn": "150710", "cntyCd": "US"}
    for scheme in ("http", "https"):
        print(f"    ④ {scheme.upper():5s} {_http(f'{scheme}://{host}{path}', params)}")

    if ips and not tcp_ok:
        print("    🚨 판정: DNS는 되지만 전 IP·전 포트 TCP 실패 → 네트워크 경로 차단 또는 "
              "러너 IP 일시 차단(대량 호출 직후 발생 시 레이트리밋 가능성 높음)")


def main() -> None:
    print("[진단] 한국 공공기관 API 호스트 연결 계층 분리 측정 (A-095)")
    for host, path in HOSTS:
        try:
            diagnose(host, path)
        except Exception as e:      # 진단 자체는 절대 잡을 실패시키지 않음
            print(f"    [경고] {host} 진단 중 예외: {type(e).__name__}: {e}")
    print("\n[안내] 위 결과를 MEMORY A-095에 기록해 재발 시 계층별 비교에 사용")


if __name__ == "__main__":
    main()
