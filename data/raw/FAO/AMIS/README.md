# FAO AMIS Market Monitor

월별 FAO AMIS(Agricultural Market Information System) Market Monitor PDF

## 파일 명명 규칙
`YY년 MM월_Market Monitor Issue.pdf`  
예: `17년 2월_Market Monitor Issue.pdf`

## 수집 범위
2017년 2월 ~ 2026년 5월

## 결측
- 매년 1월, 8월 발행 없음
- 2017년: 1월, 3월, 8월 없음

## 처리 방법
LLM 기반 추출 (Claude claude-sonnet-4-6) → `scripts/ingest_fao_amis_pdf.py`
규칙 기반 파싱 불가 (PDF 레이아웃이 연도별로 다름)

## 주요 추출 지표
- 글로벌 식물성 유지류 공급/수요 밸런스
- 대두유 생산·소비·재고 전망
- 주요 리스크 요인 텍스트
