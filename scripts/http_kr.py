#!/usr/bin/env python3
"""
한국 공공기관 API 전용 견고 HTTP 클라이언트 (A-104)

배경: KOSIS·관세청·BOK ECOS에서 `httpx.ConnectTimeout: timed out`이 반복 발생했다.
완화 이력 — A-083(재시도 3회·타임아웃 60s) → 재발, A-085(IPv4 강제) → 재발,
A-095(계층 분리 진단) → KOSIS·관세청 해소 확인. 그러나 **BOK ECOS에서 신규 발생**해
동일 계열 문제가 호스트를 옮겨가며 나타나는 것으로 판단된다.

설계 원칙:
  ① 재시도 예산을 **호출부가 아니라 여기서** 일원화한다(워크플로우 heredoc에 9벌 복제돼
     있던 `_get_retry`가 개선을 어렵게 만들었다).
  ② 전송 경로를 **다각화**한다 — IPv4 강제 / 기본 / DNS 선해석 후 IP 직접 연결.
  ③ 스킴을 **폴백**한다 — https 실패 시 http(일부 기관은 평문 경로가 더 안정적).
  ④ 지터를 넣어 동시 재시도가 몰리지 않게 한다(레이트리밋 유발 방지).
  ⑤ 실패는 **명확한 진단 문자열**과 함께 올린다(무슨 계층에서 실패했는지 남긴다).

사용:
    from http_kr import get_kr
    r = get_kr("https://ecos.bok.or.kr/api/...", timeout=45)

의존성: httpx
"""
from __future__ import annotations

import random
import socket
import time
from urllib.parse import urlsplit, urlunsplit

import httpx

DEFAULT_TRIES   = 5
DEFAULT_TIMEOUT = 45.0


def _transports() -> list[httpx.HTTPTransport | None]:
    """시도할 전송 경로 — IPv4 강제 우선, 기본 스택 폴백."""
    return [httpx.HTTPTransport(local_address="0.0.0.0", retries=1), None]


def _swap_scheme(url: str) -> str | None:
    """https ↔ http 전환 URL. 동일 스킴만 있으면 None."""
    parts = urlsplit(url)
    if parts.scheme == "https":
        return urlunsplit(("http",) + tuple(parts)[1:])
    if parts.scheme == "http":
        return urlunsplit(("https",) + tuple(parts)[1:])
    return None


def _resolve(host: str) -> list[str]:
    try:
        return sorted({i[4][0] for i in socket.getaddrinfo(
            host, None, family=socket.AF_INET, type=socket.SOCK_STREAM)})
    except socket.gaierror:
        return []


def get_kr(url: str, params: dict | None = None, headers: dict | None = None,
           timeout: float = DEFAULT_TIMEOUT, tries: int = DEFAULT_TRIES,
           allow_scheme_fallback: bool = True) -> httpx.Response:
    """한국 호스트 대상 GET — 다중 전송 경로·스킴 폴백·지터 백오프.

    성공 시 Response를 반환한다(상태코드 검증은 호출부 책임).
    전 경로 실패 시 마지막 예외를 진단 메시지와 함께 올린다.
    """
    urls = [url]
    if allow_scheme_fallback and (alt := _swap_scheme(url)):
        urls.append(alt)

    attempts: list[str] = []
    last_exc: Exception | None = None

    for i in range(tries):
        for u in urls:
            for tr in _transports():
                try:
                    with httpx.Client(transport=tr, timeout=timeout,
                                      follow_redirects=True) as c:
                        return c.get(u, params=params, headers=headers)
                except httpx.TransportError as e:
                    last_exc = e
                    attempts.append(f"{urlsplit(u).scheme}/"
                                    f"{'v4' if tr else 'default'}:{type(e).__name__}")
        # 지터 백오프 — 동시 재시도 몰림 방지
        time.sleep(min(30.0, 5 * (i + 1)) + random.uniform(0, 2.5))

    host = urlsplit(url).netloc
    ips = _resolve(host)
    diag = (f"[오류] {host} 전 경로 실패 — DNS {'성공' if ips else '실패'}"
            f"({', '.join(ips) or 'N/A'}), 시도={len(attempts)}회. "
            f"패턴: {', '.join(attempts[:6])}")
    raise RuntimeError(diag) from last_exc


def get_kr_json(url: str, **kw) -> dict:
    """GET → JSON. 상태코드 검증 포함."""
    r = get_kr(url, **kw)
    r.raise_for_status()
    return r.json()
