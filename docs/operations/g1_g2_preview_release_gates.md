# G1 / G2 Preview Release Gates

이 문서는 외부 데이터 전용 파이프라인의 재현 가능한 릴리스 기준을 정의한다. 계정명, 구독명,
네트워크 토폴로지, 개인 일정, 비밀정보는 기록하지 않는다.

## 현재 판정

- **G1**: canonical CBOT 세션 타깃과 핵심 피처가 준비도 게이트를 통과한 뒤에만 실행한다.
- **G2 Preview**: G1의 동일 snapshot을 사용하는 오프라인 배치 잡으로 한정한다 — 2026-09-02 개정: 실행 표면은 **현 CI CPU 임시 예외**(재현 조건: 동일 스냅샷에서 이관 표면 재실행 시 지표 차 <0.5%). 구 'Azure ML Command job' 표기는 Azure 폐지로 무효.
- **운영 G2/G3, 실시간 endpoint, Snowflake 전환**: Preview의 선행조건이 아니다.

현재 Databento `ohlcv-1d` 산출물은 UTC 날짜 버킷이다. CME 거래 세션 종가나 공식 정산가가
아니므로 `CBOT_BO_UTC_*` 진단 계열로만 사용한다. `CBOT_BO_CLOSE`는 다음 중 하나를 만족한
별도 원천만 발행할 수 있다.

1. intraday trades/OHLCV를 CME 세션 경계와 휴일 캘린더로 재집계한 계열
2. 거래소 공식 settlement와 표본 교차검증을 통과한 계열

Sunday 값을 Monday로 단순 이동하는 방식은 한 UTC 버킷이 거래 세션을 나누는 문제를 해결하지
못하므로 허용하지 않는다.

## 구현 우선순위와 현재 장애물

| 우선순위 | 항목 | 이번 변경 | 완료 판정 |
|---|---|---|---|
| P0 | canonical target 의미 오류 | UTC 계열을 `CBOT_BO_UTC_*`로 격리하고 fallback 차단 | 세션/settlement 표본 교차검증 통과 |
| P0 | fail-open workflow | as-of·비정형·DQ·artifact 경로를 fail-closed로 연결 | 실패 주입 시 G1 job 미실행 |
| P0 | 시점 누수 | `available_at` ASOF mart와 fold 내부 전처리 강제 | 독립 pandas 재계산 및 시간분할 테스트 통과 |
| P1 | G1 재현성 | 단일 feature mart/contract만 입력으로 허용 | 동일 snapshot에서 보고서 재생성 |
| P1 | Azure 이관 | OIDC, SHA256 manifest, 업로드 왕복 검증, 성공 marker | `_SUCCESS.json`이 마지막에 생성 |
| P1 | G2 Preview | 현재 실행 코드가 없으므로 최소 champion/baseline 구현 필요 | 아래 Preview 완료 정의 전 항목 충족 |
| P2 | 운영 확장 | 실시간 endpoint·고급 challenger·별도 warehouse 적재 | Preview 이후 별도 승인 |

현재 저장소에 추가된 것은 P0/P1 릴리스 기반이다. canonical 세션/정산 원천 확보와 Azure ML
G2 학습 스크립트·Command job은 외부 시스템 검증이 필요한 미완료 항목이므로 문서만으로 완료 처리하지
않는다.

## 필수 게이트

| 순서 | 게이트 | 통과 기준 | 실패 동작 |
|---:|---|---|---|
| 1 | 수집 | 키·의존성·전체 구간 수집 성공, 필수 파일 생성 | 비정상 종료 |
| 2 | C-08 DQ | 빈 파일 없음, 필수 산출물 존재, 타깃 계약 통과 | 후속 job 중단 |
| 3 | as-of | `event_time`/`available_at` 결측·역전 0건 | 모델 진입 중단 |
| 4 | readiness | 타깃 세션 커버리지 ≥98%, 핵심 피처 월 커버리지 ≥85% | G1/G2 중단 |
| 5 | feature mart | DuckDB ASOF와 pandas 표본 재계산 일치 | 산출물 미발행 |
| 6 | G1 | `target_ret{1,5,20,60}` 명시, TimeSeriesSplit, fold 내부 전처리 | 보고서 미발행 |
| 7 | Blob snapshot | 파일별 SHA256·행수·스키마 확인 후 `_SUCCESS.json` 생성 | snapshot 소비 금지 |

타깃 계약은 다음 값을 모두 요구한다.

- `indicator_code`: `CBOT_BO_CLOSE` 또는 승인된 canonical alias
- `target_eligible`: `true`
- `time_basis`: `CME_SESSION` 또는 `EXCHANGE_SETTLEMENT`
- `unit`: `USc/lb`
- 주말 날짜 0건, 세션당 1건, 양수 가격, as-of 역전 0건

## 실행 순서

1. Pull Request에서 `Pull Request Quality Gate`를 통과시킨다.
2. Historical/Data Integration workflow로 외부 데이터 아티팩트를 생성한다.
3. workflow 내부의 Model Readiness job이 feature mart와 contract를 생성한다.
4. G1 job은 raw 파일을 직접 피벗하지 않고 `data/gold/feature_mart.parquet`만 모델 입력으로 쓴다.
5. 스냅샷 발행 잡(S3 — 구 Azure Storage 워크플로우는 DEPRECATED)에 원천 run ID를 전달한다.
6. 학습 잡은 `_SUCCESS.json`이 존재하고 manifest 해시가 일치하는 snapshot만 입력으로 등록한다(2026-09-02: Azure ML Data Asset → S3 스냅샷 매니페스트).

## 실행 표면·인증 계약 (2026-09-02 개정 — 구 'Azure 인증 계약')

실행 표면은 컴퓨트 중립이다(ETL#2 Python 배치 · Dev EC2 · 병행 운전 창의 Actions). 클라우드 인증은
IAM 역할(OIDC federation 또는 인스턴스 프로파일)을 사용하며 저장소에는 값이 아닌 변수명만 둔다.
시크릿은 AWS Secrets Manager `nexus/{prd,dev}/{api,llm,snowflake}/{ENV명}`에서 `os.environ` 규약으로 주입한다.

| 종류 | 이름 | 용도 |
|---|---|---|
| Secret | `AZURE_CLIENT_ID` | federated application |
| Secret | `AZURE_TENANT_ID` | Entra tenant |
| Secret | `AZURE_SUBSCRIPTION_ID` | Azure login scope |
| Variable | `AZURE_STORAGE_ACCOUNT_URL` | Blob service URL |
| Variable | `AZURE_STORAGE_CONTAINER` | 외부 모델 데이터 컨테이너 |
| Variable | `AZURE_STORAGE_PREFIX` | immutable snapshot prefix |

권한은 컨테이너 범위의 최소 데이터 역할로 제한한다. 장기 account key와 connection string은 사용하지
않는다. 공개 네트워크 도달 가능 여부와 Blob 데이터 권한은 별개이므로 업로드·다운로드 해시 왕복을
반드시 확인한다.

## G2 Preview 완료 정의

G2 Preview는 다음 최소 범위만 완료로 인정한다.

- 오프라인 배치 잡(컴퓨트 중립 — 2026-09-02 개정)
- last-value·seasonal-naive baseline
- 단일 quantile/conformal champion
- 1·5·20일 P10/P50/P90; 60일은 데이터 게이트 통과 시 추가
- expanding walk-forward 평가
- MAE, pinball loss, empirical coverage, interval width
- MLflow run 및 입력 snapshot ID 기록
- 정적 HTML/JSON 평가 산출물

실시간 endpoint, 자동 Buy/Hold, deep-learning challenger, Snowflake 적재는 Preview 완료 조건이 아니다.

## Merge 금지 조건

- 필수 단계에 `--warn`, `|| true`, `continue-on-error` 사용
- C-08 실패 후 `if: always()`로 G1 실행
- CBOT 부재 시 Brent/CPO/첫 컬럼을 타깃으로 대체
- raw parquet를 `price_date`로 직접 pivot하여 모델 입력으로 사용
- UTC 일봉을 CME 세션/settlement로 표기
- 생성 데이터·보고서를 workflow에서 main에 직접 push
- `_SUCCESS.json` 없는 스냅샷 prefix(S3)를 학습 잡이 소비
