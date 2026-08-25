# 아웃바운드 방화벽 허용 신청서 (제출용) — Project Nexus

**신청 부서**: 구매/조달 · **작성**: 2026-08-25 (v2.3 — 일별·거시 매체 5종 추가) · **제출 목표**: 2026-08-29
**근거 문서**: `docs/infra/egress_allowlist.yaml` (v2.3)

## 신청 개요

- 총 **47개 호스트** — 전량 아웃바운드 전용(인바운드 없음), 대부분 443/TLS
- 사유: 대두유 조달 의사결정 AI(Project Nexus)의 외부 데이터 수집
- 미승인 시: 11월 통합 시점에 해당 데이터 수집이 즉시 중단됨

## 별도 협의 필요 (3건)

| 호스트 | 사유 | 미승인 시 |
|---|---|---|
| `apis.data.go.kr` | 평문 HTTP 80 | 관세청 수출입실적(대두유 + 대체·보완재 16 HS × 10개국) 수집 불가 — 도착가 실측 기반 소멸 |
| `stream.aisstream.io` | WebSocket(wss) — HTTP 프록시로 통과 불가 | 해협 탱커 추적 상실 — Perplexity 프록시로 대체(정밀도 저하, 치명 아님) |
| `{storage-account}.blob.core.windows.net + login.microsoftonline.com` | 조건부 신규 — 9월 Azure Blob 이관 시 필요(D-028) | 9월 모델 스냅샷 이관 불가 — Actions 종료(11월) 후 실행 표면 상실 |

## 신청 목록

| # | 호스트 | 포트 | 중요도 | 용도 |
|---|---|---|---|---|
| 1 | `hist.databento.com` | 443 | 필수 | CBOT 대두유 선물 |
| 2 | `api.stlouisfed.org` | 443 | 필수 | FRED |
| 3 | `apis.data.go.kr` | 80 ⚠️평문 | 필수 | 관세청 GW 수출입실적 |
| 4 | `archive-api.open-meteo.com` | 443 | 필수 | ERA5-Land 12개 생산지역 일별 기후 |
| 5 | `pypi.org` | 443 | 필수 | Python 패키지 설치 |
| 6 | `files.pythonhosted.org` | 443 | 필수 | PyPI 아티팩트 다운로드 |
| 7 | `www.matteoiacoviello.com` | 443 | 높음 | Caldara-Iacoviello GPR 지수 |
| 8 | `api.tradingeconomics.com` | 443 | 높음 | BDI · CPO 실시간 갱신 |
| 9 | `api.eia.gov` | 443 | 높음 | Brent 원유 |
| 10 | `api.fas.usda.gov` | 443 | 높음 | USDA FAS PSD · ESR |
| 11 | `quickstats.nass.usda.gov` | 443 | 높음 | NASS 미국 대두 생산·수확 실적 |
| 12 | `www.cpc.ncep.noaa.gov` | 443 | 높음 | NOAA CPC ENSO ONI |
| 13 | `power.larc.nasa.gov` | 443 | 높음 | NASA POWER 농업기상 |
| 14 | `api.openai.com` | 443 | 높음 | 교차검증 |
| 15 | `api.anthropic.com` | 443 | 높음 | 에이전트 오케스트레이션 · LLM 모델 모니터 |
| 16 | `api.perplexity.ai` | 443 | 보통 | 실시간 비정형 프록시 |
| 17 | `ecos.bok.or.kr` | 443 | 보통 | 한국은행 ECOS |
| 18 | `kosis.kr` | 443 | 보통 | 한국 CPI |
| 19 | `api.bcra.gob.ar` | 443 | 보통 | 아르헨티나 ARS 환율 |
| 20 | `fenixservices.fao.org` | 443 | 보통 | FAOSTAT 생산·교역 장기 시계열 |
| 21 | `usdmdataservices.unl.edu` | 443 | 보통 | US Drought Monitor D0–D4 |
| 22 | `api.weather.gov` | 443 | 보통 | NOAA 기상경보 |
| 23 | `api.gdeltproject.org` | 443 | 보통 | GDELT 이벤트 |
| 24 | `stream.aisstream.io` | 443 (wss) | 보통 | 해협 탱커 추적 |
| 25 | `www.policyuncertainty.com` | 443 | 보통 | GPR 최후 폴백 · EPU 지수 |
| 26 | `stooq.com` | 443 | 보통 | BDI 폴백 |
| 27 | `farmdocdaily.illinois.edu` | 443 | 보통 | farmdoc daily RSS |
| 28 | `www.world-grain.com` | 443 | 보통 | World Grain RSS |
| 29 | `www.ofimagazine.com` | 443 | 보통 | OFI |
| 30 | `grain.org` | 443 | 낮음 | GRAIN RSS |
| 31 | `igc.int` | 443 | 낮음 | 국제곡물이사회 |
| 32 | `soygrowers.com` | 443 | 낮음 | 미 대두협회 |
| 33 | `www.climatepol.com` | 443 | 낮음 | 크라이미트폴 RSS |
| 34 | `query1.finance.yahoo.com` | 443 | 낮음 | yfinance ZL=F 정산가 |
| 35 | `query2.finance.yahoo.com` | 443 | 낮음 | 동일 |
| 36 | `comtradeapi.un.org` | 443 | 낮음 | UN Comtrade |
| 37 | `apps.fas.usda.gov` | 443 | 낮음 | USDA 구 OpenData 호스트 |
| 38 | `api.ers.usda.gov` | 443 | 낮음 | ERS ARMS 생산비용 |
| 39 | `data.ers.usda.gov` | 443 | 낮음 | ARMS 구 호스트 |
| 40 | `apis.datos.gob.ar` | 443 | 낮음 | 아르헨티나 INDEC 생산 시계열 |
| 41 | `api.openweathermap.org` | 443 | 낮음 | 현재 기상 |
| 42 | `earthquake.usgs.gov` | 443 | 낮음 | USGS 지진 |
| 43 | `firms.modaps.eosdis.nasa.gov` | 443 | 낮음 | NASA FIRMS 산불 |
| 44 | `data.nasdaq.com` | 443 | 낮음 | 레거시 조회 |
| 45 | `fonts.googleapis.com` | 443 | 낮음 | 리포트 웹폰트 |
| 46 | `huggingface.co` | 443 | 낮음 | 임베딩 모델 메타데이터 |
| 47 | `cdn-lfs.huggingface.co` | 443 | 낮음 | 모델 가중치 파일 |

## 텍스트 목록 (시스템 입력용)

```
hist.databento.com:443
api.stlouisfed.org:443
apis.data.go.kr:80
archive-api.open-meteo.com:443
pypi.org:443
files.pythonhosted.org:443
www.matteoiacoviello.com:443
api.tradingeconomics.com:443
api.eia.gov:443
api.fas.usda.gov:443
quickstats.nass.usda.gov:443
www.cpc.ncep.noaa.gov:443
power.larc.nasa.gov:443
api.openai.com:443
api.anthropic.com:443
api.perplexity.ai:443
ecos.bok.or.kr:443
kosis.kr:443
api.bcra.gob.ar:443
fenixservices.fao.org:443
usdmdataservices.unl.edu:443
api.weather.gov:443
api.gdeltproject.org:443
stream.aisstream.io:443
www.policyuncertainty.com:443
stooq.com:443
farmdocdaily.illinois.edu:443
www.world-grain.com:443
www.ofimagazine.com:443
grain.org:443
igc.int:443
soygrowers.com:443
www.climatepol.com:443
query1.finance.yahoo.com:443
query2.finance.yahoo.com:443
comtradeapi.un.org:443
apps.fas.usda.gov:443
api.ers.usda.gov:443
data.ers.usda.gov:443
apis.datos.gob.ar:443
api.openweathermap.org:443
earthquake.usgs.gov:443
firms.modaps.eosdis.nasa.gov:443
data.nasdaq.com:443
fonts.googleapis.com:443
huggingface.co:443
cdn-lfs.huggingface.co:443
```

## 추후 추가 예정 (9월 Azure 이관 확정 시)

- `login.microsoftonline.com` :443 — Azure OIDC 인증(azure/login)
- `{storage-account}.blob.core.windows.net` :443 — 모델 스냅샷 업로드(불변 스냅샷·SHA256 매니페스트)

## 신청 제외

- `cds.climate.copernicus.eu` — CDS v2 API 폐기(A-083) 후 기후 실수집원은 Open-Meteo ERA5-Land로 전환됨(A-100). 코드 어디에서도 호출하지 않으므로 신청 대상에서 제외한다.
