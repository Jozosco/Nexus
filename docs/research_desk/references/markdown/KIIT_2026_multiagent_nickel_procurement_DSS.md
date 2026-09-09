# KIIT_2026_multiagent_nickel_procurement_DSS

> 원본: `docs/research_desk/references/KIIT_2026_multiagent_nickel_procurement_DSS.pdf` · SHA256 `255959da0db40844…` · 12쪽 · 22,389자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
- 멀티 AI 에이전트 기반 니켈 조달 의사결정지원시스템 (p.1)
  - 프레임워크 설계 및 개발 (p.1)
    - Design and Development of a Multi-AI Agent-based Framework (p.1)
    - for a Nickel Procurement Decision Support System (p.1)

## 표(자동 추출)
**표 p.4**

| Agent | Primary role | Input data | Core processing |
|---|---|---|---|
| Planning agent | Scenario generation | Estimated inventory info | Rule-based planning |
| Purchase agent | Price trend analysis | Market & macro data | ML forecasting |
| Customs agent | Import risk identification | Trade & regulation info | Knowledge retrieval |
| Logistics agent | Logistics monitoring | Logistics event data | Event monitoring |
| Quality agent | Nickel quality check | Quality documents | Document summary |
| Finance agent | Financial risk estimation | Cost & exchange data | Cost calculation |
| Inventory agent | Inventory risk review | Stock & usage data | Time-series analysis |

**표 p.8**

| Model | CV RMSE | Test RMSE | Test R² | Test MAE | Test MAPE |
|---|---|---|---|---|---|
| Linear | 1057.04 | 665.60 | 0.94 | 481.67 | 2.63 |
| Lasso | 886.90 | 827.64 | 0.91 | 692.05 | 3.96 |
| Ridge | 879.57 | 784.30 | 0.92 | 620.42 | 3.47 |
| Elastic net | 908.22 | 797.70 | 0.92 | 634.04 | 3.55 |
| RF | 1776.89 | 1348.67 | 0.77 | 923.33 | 4.83 |
| AdaBoost | 1682.56 | 1269.87 | 0.80 | 889.05 | 4.67 |
| XGBoost | 1811.98 | 1151.32 | 0.83 | 808.16 | 4.29 |
| LightGBM | 1832.38 | 1231.67 | 0.81 | 900.61 | 4.85 |

## 본문

<!-- page 1 -->

Journal of KIIT. Vol. 24, No. 7, pp. 287-298, Jul. 31, 2026. pISSN 1598-8619, eISSN 2093-7571 287 \ * 명지대학교 경영정보학과 학부과정 - ORCID1: https://orcid.org/0009-0000-2354-4471 - ORCID2: https://orcid.org/0009-0007-7467-8171 - ORCID3: https://orcid.org/0009-0003-6094-4556 ** 명지대학교 경영정보학과 부교수(교신저자) - ORCID: https://orcid.org/0000-0002-9005-3661 ž Received: Apr. 08, 2026, Revised: May 23, 2026, Accepted: May 26, 2026 ž Corresponding Author: Hanjun Lee Dept. of Management Information Systems, Myongji University, Korea Tel.: +82-2-300-0772, Email: hjlee1609@gmail.com

## 멀티 AI 에이전트 기반 니켈 조달 의사결정지원시스템


### 프레임워크 설계 및 개발

김선오*1, 유지현*2, 권가영*3, 이한준**

#### Design and Development of a Multi-AI Agent-based Framework


#### for a Nickel Procurement Decision Support System

Seono Kim*1, Jihyeon Ryu*2, Gayeong Kwon*3, and Hanjun Lee** 요  약 가격 변동성과 구조적 공급 제약으로 인해 니켈 조달 환경에서는 구매 의사결정의 불확실성이 높게 나타난 다. 이에 본 연구는 멀티 AI 에이전트 기반 니켈 조달 의사결정지원시스템 프레임워크를 설계·개발하였다. 기 존 니켈 구매 방식은 개별 분석이나 단일 예측 모델에 의존하는 경우가 많아, 다양한 시장 요인과 재고 상황 을 종합적으로 반영하는 데 한계가 있다. 제안 프레임워크는 사용자 가정 기반으로 재고 커버리지와 발주 시 점을 산출하는 계획 모듈, 가격 예측 및 시장 요인 분석을 수행하는 역할 기반 분석 에이전트, 분석 결과를 통 합해 구매 판단을 지원하는 오케스트레이션 에이전트로 구성된다. 구현 및 시나리오 평가 결과, 제안 프레임워 크는 실시간 정보가 제한된 환경에서도 데이터를 활용해 구매 의사결정을 구조적으로 지원함을 확인하였다.
Abstract This study designs and develops a multi-AI-agent-based decision support framework for nickel procurement under uncertain market and inventory conditions. Nickel procurement is characterized by high price volatility and structural supply constraints, making integrated decision-making increasingly challenging. The framework consists of a planning module that computes inventory coverage and order timing based on user-defined assumptions, role-based analysis agents that perform price forecasting and market factor analysis, and an orchestration agent that coordinates agent execution and integrates their outputs. Implementation and scenario-based evaluation demonstrate that the framework supports structured and context-aware procurement decision-making when real-time information is limited.
Keywords decision support system, multi-AI agent framework, procurement, price forecasting, scenario-based evaluation http://dx.doi.org/10.14801/jkiit.2026.24.7.287

<!-- page 2 -->

288 멀티AI 에이전트기반니켈조달의사결정지원시스템프레임워크설계및개발 Ⅰ. 서  론 니켈은 이차전지, 스테인리스강 등 다양한 산업 에서 핵심적인 원자재로 활용되며, 글로벌 산업 전 반의 안정적인 생산을 위해 필수적인 자원이다. 그 러나 니켈은 특정 국가 및 지역에 생산이 편중되어 있고, 재활용 효율 또한 제한적인 수준에 머물러 있 어 구조적인 공급 제약을 지닌 금속으로 분류된다 [1]. 이러한 특성으로 인해 니켈 시장은 지정학적 리스크, 정책 변화, 글로벌 경기 변동에 민감하게 반응하며, 가격 변동성과 공급 불확실성이 지속적으 로 확대되고 있다.
공급망 관리 관점에서 니켈 조달 환경은 다수의 위험 요인이 동시에 작용하는 취약한 구조를 가진 다. 니켈 산업사슬 관련 연구에서는 글로벌 니켈 공 급과 수요의 공간적 불균형, 특정 국가에 집중된 매 장량 및 생산 구조, 국제무역 의존성, 니켈광 및 관 련 제품의 무역가격 변동 위험이 니켈 공급 안정성 에 영향을 미치는 주요 요인으로 제시되었다[2]. 기 존 연구에서는 불확실성이 높은 환경에서 공급망을 단일 흐름이 아닌 상호의존적 네트워크로 인식하고, 외부 충격 발생 시에도 기능을 유지하거나 회복할 수 있는 회복탄력성을 핵심 관리 요소로 제시하였 다[3]. 또한 공급망 취약성과 위험은 개별 사건이 아니라 구조적 특성에서 기인하며, 이를 완화하기 위해서는 단일 위험 요인이 아닌 복수의 위험을 통 합적으로 고려하는 관리 전략이 필요함을 논의하였 다[4]. 이러한 관점에서 공급망 위험 관리는 개별 변수에 기반한 판단이 아니라, 다양한 위험 요인을 종합적으로 반영하는 의사결정 프레임워크를 요구 한다[5]. 니켈 원자재 조달은 이러한 공급망 위험 관리 특성이 집약적으로 나타나는 대표적인 사례라 할 수 있다.
기존의 니켈 구매 의사결정 방식은 주로 가격 예 측 결과나 과거 경험에 기반한 규칙적 판단에 의존 해 왔다. 최근에는 딥러닝 기반 시계열 예측 기법을 활용하여 원자재 가격을 보다 정교하게 예측하려는 연구가 확산되고 있으며, 다변량 외생 변수를 반영 한 예측 모델들이 제안되고 있다[6]. 국내에서도 액 체 신경망(Liquid neural network)을 활용한 니켈 가 격 예측 연구가 수행되어, 가격 변동성 예측 측면에 서의 가능성이 보고된 바 있다[7]. 그러나 이러한 연구들은 주로 가격 예측 성능의 향상에 초점을 두 고 있어, 실제 구매 시점 결정이나 재고 수준, 조달 전략을 함께 고려하는 종합적인 의사결정 지원으로 의 확장에는 한계를 가진다.
실제 구매 의사결정 과정에서는 가격 전망뿐만 아니라 현재 재고 수준, 예상 수요, 발주 리드타임, 시장 리스크 등 다양한 요소가 동시에 고려되어야 한다. 특히 실무 환경에서는 실시간 재고 데이터가 항상 확보되지 않거나, 불완전한 정보에 기반해 의 사결정을 내려야 하는 상황이 빈번하게 발생한다.
이러한 환경에서는 단일 예측 모델이나 개별 분석 결과만으로는 구매 의사결정을 효과적으로 지원하 기 어렵다.
이에 본 논문에서는 니켈 구매 의사결정의 복잡 성과 불확실성을 완화하기 위해, 멀티 AI 에이전트 기반 의사결정지원시스템(DSS, Decision Support System) 프레임워크를 설계 및 개발하였다. 제안된 프레임워크는 사용자 가정을 기반으로 재고 커버리 지와 발주 시점을 산출하는 계획 모듈과, 가격 예측 및 시장 요인 분석을 수행하는 역할 기반 분석 에 이전트, 그리고 이들 결과를 통합하여 구매 판단을 지원하는 오케스트레이션 에이전트(Orchestration agent)로 구성된다. 이를 통해 가격 예측 중심의 기 존 접근을 넘어, 실제 구매 의사결정 맥락을 반영한 구조적이고 일관된 의사결정 지원을 목표로 한다.
Ⅱ. 선행연구 의사결정지원시스템은 복잡하고 비정형적인 문제 환경에서 의사결정자의 판단을 지원하기 위한 정보시 스템이다. 이러한 시스템은 다양한 분석 결과를 통합 하여 의사결정 과정을 보조하는 것을 목적으로 한다.
최근 대규모 언어 모델(LLM, Large Language Model)의 발전과 함께 복잡한 의사결정 문제를 지원 하기 위한 다양한 접근이 등장하였다. 하나의 흐름 은 RAG(Retrieval-Augmented Generation)과 같이 단일 모델에 외부 지식 검색 메커니즘을 결합하는 방식 이다[8]. 이러한 접근은 응답 품질 향상에 기여하였 으나, 기본적으로 하나의 통합 모델 내에서 동작하 기 때문에 역할 기반 기능 분업이나 실행 흐름 조

<!-- page 3 -->

Journal of KIIT. Vol. 24, No. 7, pp. 287-298, Jul. 31, 2026. pISSN 1598-8619, eISSN 2093-7571 289 정 구조를 명시적으로 포함하지 않는다.
이에 따라 선행연구는 복잡한 문제를 구조적으로 분해하고 기능을 분산 처리하기 위한 멀티 에이전 트 기반 접근을 대안으로 제시하였다[9][10]. 이러한 구조에서는 분석 기능을 역할 단위로 분리하고, 상 위 수준에서 이를 선택·조정하는 계층적 메커니즘 을 통해 의사결정 과정을 체계화한다[11]. 특히 멀 티 에이전트 환경에서는 에이전트 간 상호작용과 실행 순서를 관리하는 오케스트레이션이 핵심 요소 로 작용하며, 관련 연구에서는 상황 인지적 라우팅 이나 계획 기반 실행 방식을 제안하였다[12].
다만 자동화된 에이전트 협업 구조만으로는 조직 의 전략적 맥락이나 도메인 특수성을 충분히 반영 하기 어렵다는 지적도 존재한다. 이러한 한계를 보 완하기 위한 연구에서는 인간의 전략적 개입을 포 함하는 인간 주도형 다중 에이전트 프레임워크를 제안하였다[13]. 이는 멀티 에이전트 구조에 인간의 판단을 결합함으로써 의사결정 품질을 보완하려는 접근으로 이해할 수 있다.
마지막으로, 복잡한 의사결정시스템의 유용성은 단일 정량 지표만으로 평가하기 어렵다. 실제 환경 에서는 정보의 불완전성과 다양한 가정이 동시에 존재하기 때문에, 시나리오 기반 평가는 시스템의 반응과 의사결정 흐름을 분석하는 데 유용하다. 예 를 들어, RAG와 멀티 에이전트를 결합한 시스템 연구에서도 사례 기반 또는 시나리오 기반 검증을 수행하였다[14]. 이러한 평가는 특정 조건 하에서 시스템의 작동 구조와 적용 가능성을 검토하는 데 적합하다.
Ⅲ. 연구 방법 본 장에서는 니켈 원자재 구매 의사결정을 지원 하기 위해 제안하는 멀티 AI 에이전트 기반 의사결 정지원시스템의 구조와 동작 원리를 설명한다. 제안 시스템은 구매 의사결정에 필요한 복수의 역할 기 반 에이전트와 이들의 실행을 조정·통합하는 오케 스트레이션 에이전트로 구성된다. 이를 통해 가격 변동성과 재고 불확실성이 높은 환경에서도 다양한 정보를 함께 고려한 일관된 의사결정 지원이 가능 하도록 설계하였다.
3.1 시스템전체구조및오케스트레이션흐름 그림 1은 본 연구에서 제안하는 멀티 AI 에이전 트 기반 니켈 구매 의사결정지원시스템의 전체 구 조를 나타낸다. 시스템은 사용자 입력을 수집하는 프론트엔드, 에이전트 실행을 조정하는 오케스트레 이션 에이전트, 구매 의사결정의 개별 관점을 담당 하는 역할 기반 전문 에이전트 집합, 그리고 각 에 이전트의 기능 수행을 지원하는 AI 기반 처리 모듈 로 구성된다.
그림1. 시스템구조 Fig. 1. Proposed system architecture

<!-- page 4 -->

290 멀티AI 에이전트기반니켈조달의사결정지원시스템프레임워크설계및개발 사용자는 현재 재고 수준, 예상 수요, 안전 재고 기준, 리드타임, 통관 조건, 품질 관련 문서 등 구 매 의사결정에 필요한 기본 정보를 입력한다. 이러 한 입력은 시스템의 공통 상태 정보로 관리되며, 이후 어떤 에이전트를 호출할지 결정하는 기준으 로 활용된다.
시스템의 중심에는 오케스트레이션 에이전트가 위치한다. 오케스트레이션 에이전트는 사용자 질의 와 공통 상태 정보를 기반으로 현재 상황에서 필요 한 전문 에이전트를 선택하고, 실행 순서를 조정하 며, 각 에이전트의 출력을 최종 의사결정 지원 형태 로 통합하는 역할을 수행한다. 즉, 모든 에이전트를 일괄적으로 실행하는 방식이 아니라, 상황에 따라 필요한 분석만을 선택적으로 수행하도록 설계하였 다. 이를 통해 개별 에이전트는 각자의 분석 기능에 집중할 수 있으며, 시스템 전체의 실행 흐름은 일관 되게 관리된다. 이때 역할 기반 에이전트의 분석 결 과가 서로 다른 방향의 판단을 제시할 경우, 오케스 트레이션 에이전트는 재고 안정성, 가격 변동성, 비 용 영향 요인을 우선순위 기준으로 비교하여 최종 권고를 통합한다. 예를 들어 재고 부족 위험이 확인 되면 생산 차질 방지를 우선 기준으로 설정하고, 가 격 추세와 재무 및 원가 분석 결과를 함께 반영하 여 즉시 구매, 선제 구매, 구매 보류 등으로 권고 방향을 조정한다.
전문 에이전트 그룹은 계획, 구매, 통관, 물류, 품 질, 재무, 재고의 일곱 개 에이전트로 구성되며, 각 각 구매 의사결정에 필요한 서로 다른 분석 관점을 담당한다. 일부 에이전트는 AI 기반 처리 모듈과 연계되어 RAG 기반 검색, 하이브리드 검색, 도구 호출, 문서 파싱, 요약, 재정렬 및 설명 가능성 분석 등의 기능을 수행한다. 예를 들어 구매 에이전트는 가격 예측과 주요 영향 요인 분석을 수행하며, 통관 및 품질 에이전트는 문서 기반 정보 검색과 요약 기능을 활용한다. 이러한 구조를 통해 시스템은 정 량적 예측 결과와 정성적 문서 정보를 함께 반영할 수 있다.
최종적으로 각 전문 에이전트의 분석 결과는 오 케스트레이션 에이전트에 의해 정리·통합되어 사용 자에게 구조화된 형태의 의사결정 지원 정보로 제 공된다. 본 시스템은 최종 구매 결정을 자동으로 수 행하는 자율 시스템이 아니라, 인간 의사결정자가 다양한 분석 결과를 종합적으로 검토할 수 있도록 지원하는 Human-in-the-loop 기반 의사결정지원시스 템을 지향한다.
3.2 역할기반에이전트구성 제안 시스템은 니켈 구매 의사결정의 복합성을 반영하기 위해 역할 기반 에이전트 구조를 채택한 다. 각 에이전트는 구매 의사결정 과정에서 요구되 는 특정 분석 관점을 담당하며, 독립적인 기능을 수 행하되 오케스트레이션 에이전트의 제어 하에 선택 적으로 호출된다. 이러한 구조는 분석 기능의 모듈 화를 가능하게 하며, 다양한 의사결정 상황에 유연 하게 대응할 수 있도록 한다.
표 1은 본 연구에서 설계한 역할 기반 에이전트 들의 주요 역할, 입력 데이터, 핵심 처리 방식을 요 약한 것이다. 각 에이전트는 서로 다른 목적을 가지 지만, 궁극적으로는 니켈 구매 판단에 필요한 근거 정보를 생성한다는 공통 목표를 가진다. 각 에이전 트의 설계 목적과 주요 기능은 다음과 같다.
표1. 역할기반에이전트구성및기능 Table 1. Role-based agents and functions Agent Primary role Input data Core processing Planning agent Scenario generation Estimated inventory info Rule-based planning Purchase agent Price trend analysis Market & macro data ML forecasting Customs agent Import risk identification Trade & regulation info Knowledge retrieval Logistics agent Logistics monitoring Logistics event data Event monitoring Quality agent Nickel quality check Quality documents Document summary Finance agent Financial risk estimation Cost & exchange data Cost calculation Inventory agent Inventory risk review Stock & usage data Time-series analysis

<!-- page 5 -->

Journal of KIIT. Vol. 24, No. 7, pp. 287-298, Jul. 31, 2026. pISSN 1598-8619, eISSN 2093-7571 291 3.2.1 계획 에이전트 계획 에이전트(Planning agent)는 구매 의사결정 이 전 단계에서의 구매 시점 및 구매 물량 계획을 지원 하는 역할을 수행한다. 본 에이전트는 수요 예측 결 과, 현재 재고 수준, 리드타임, 안전 재고 기준을 입 력으로 받아 복수의 구매 시나리오를 생성한다.
생성된 시나리오는 규칙 기반 계획 로직을 통해 계산되며, 이후 구매 에이전트의 가격 분석 결과와 결합되어 구매 판단을 위한 기준 정보로 활용된다.
3.2.2 구매 에이전트 구매 에이전트(Purchase agent)는 본 연구에서 제 안하는 멀티 AI 에이전트 기반 의사결정지원시스템 의 핵심 분석 에이전트로, 니켈 구매 의사결정에서 가장 중요한 가격 변동 방향을 예측하고 그 원인을 해석하는 역할을 담당한다.
본 에이전트는 인베스팅닷컴(Investing.com)을 통 해 수집한 LME 니켈 일별 종가 데이터를 중심으 로, 주요 원자재의 일별 종가 및 거래량, 한국석유 공사가 운영하는 석유정보망 페트로넷(Petronet)에서 수집한 유가 변수, 거시경제 지표, 금융시장 지표를 포함한 다변량 시계열 데이터를 입력으로 활용한다.
본 연구에서는 2012년 1월부터 2025년 10월 31일까 지의 데이터를 수집하였으며, 총 5,025개의 일별 관 측치를 확보하였다. 전체 데이터는 니켈 가격을 포 함한 17개의 최종 입력 변수로 구성된다.
변수별 데이터 생성 빈도가 상이하므로 일별 시 계열 정렬 과정이 수행되었다. 니켈 가격 및 주요 원자재·금융 지표와 같은 연속형 일별 변수에 대해 서는 선형 보간(Linear interpolation)을 적용하여 결 측 구간을 보완하였다. 반면 PMI, CPI, PPI 등 월별 또는 비정기적으로 발표되는 거시경제 지표는 발표 일 기준 데이터를 수집한 후, 일별 데이터와 정렬하 기 위해 이전 값 유지 방식(Forward fill)을 적용하였 으며, 경계 구간의 결측치는 이후 값 유지 방식 (Backward fill)을 통해 보완하였다.
또한 변수 간 상관 구조를 반영하기 위해 일부 지표에 주성분분석(PCA, Principal Component Analysis)을 적용하였으며, 이후 각 변수에 대해 시 차(Lag) 변수와 이동 통계(Rolling statistics) 기반 파 생변수를 생성하였다.
본 연구에서는 기준 시점(t)을 기준으로 7일 후의 니켈 종가를 예측하는 구조를 채택하였다. 이는 예 측 기간에 따라 모델의 성능과 요구되는 구조가 달 라진다는 기존 연구를 반영한 것이다[15][16]. 따라 서 본 연구에서는 실제 구매 의사결정에 활용 가능 한 단기 예측에 초점을 맞추어 7일 예측 기간을 설 정하였다.
전체 데이터는 시계열 특성을 고려하여 과거 구 간을 학습데이터(80%)로, 최근 구간을 테스트 데이 터(20%)로 분할하였으며, 학습 구간에서는 TimeSeriesSplit (n_splits=5)를 적용하여 시간 순서를 유지한 5-fold 교차검증을 수행하였다.
구매 에이전트는 단순한 가격 예측 값 제공을 넘 어, 예측 결과의 배경이 되는 주요 요인을 함께 제 시함으로써 실무적 해석 가능성을 확보하도록 설계 되었다. 구매 에이전트의 내부 처리 흐름은 데이터 전처리, 모델 학습 및 선택, 성능 평가, 그리고 예측 결과의 설명 가능성 확보 단계로 구성되며, 해당 전 체 흐름은 그림 2에 개략적으로 제시하였다. 구매 에이전트의 구체적인 모델 구성과 성능 평가, 그리 고 예측 결과를 의사결정 지원 정보로 확장하는 과 정은 4.4절에서 상세히 설명한다.
3.2.3 통관 에이전트 통관 에이전트(Customs agent)는 수입 과정에서 발생할 수 있는 통관 및 규제 관련 리스크를 식별 하는 역할을 수행한다. 본 에이전트는 공공데이터포 털(data.go.kr)에서 제공하는 관세청 국가별 관세율 표, 품목번호별 관세율표 및 HS 부호 데이터를 활 용하여 HS 코드와 원산지 정보를 입력으로 받고, 관련 규제 문서를 대상으로 RAG 기반 정보 검색을 수행한다. 이를 통해 특정 국가 또는 품목에 대한 통관 이슈 가능성과 MFN 관세율 정보를 정성적으 로 요약하여 제공하며, 해당 결과는 구매 리스크 판 단을 보조하는 정보로 활용된다.

<!-- page 6 -->

292 멀티AI 에이전트기반니켈조달의사결정지원시스템프레임워크설계및개발 그림2. 구매에이전트구축을위한파이프라인 Fig. 2. Pipeline for the purchase agent 3.2.4 품질 에이전트 품질 에이전트(Quality agent)는 니켈 원자재의 품 질 적합성을 검토하는 역할을 수행한다. 본 에이전 트는 검사 성적서 및 품질 인증서와 같은 문서 자 료를 입력으로 활용하여 문서 기반 요약 분석 및 품질 기준 충족 여부를 판단한다. 해당 결과는 구매 리스크 평가를 보조하는 정보로 활용된다.
3.2.5 물류 에이전트 물류 에이전트(Logistics agent)는 운송 단계에서 발생할 수 있는 물류 이벤트를 모니터링하는 역할 을 담당한다. 본 에이전트는 선적 상태, 운송 경로, 지연 이벤트 등의 정보를 입력으로 활용하여 물류 지연 가능성을 탐지한다. 해당 분석 결과는 리드타 임 불확실성 요인으로서 구매 시점 결정 과정에 반 영된다.
3.2.6 재무 에이전트 재무 에이전트(Finance agent)는 구매 시점 및 조 건에 따른 재무적 영향을 추정하는 에이전트이다.
본 에이전트는 환율 정보, 원가 구조, 세금 규칙 등 을 입력으로 받아 니켈 원자재 구매 시점별 비용 변화를 수치적으로 계산한다. 이에 서로 다른 구매 시나리오 간의 재무적인 평가를 확인할 수 있다.
3.2.7 재고 에이전트 재고 에이전트(Inventory agent)는 현재 재고 상태 와 향후 소비 패턴을 기반으로 재고 리스크를 평가 하는 에이전트이다. 본 에이전트는 현재 재고 수준, 소비율, 안전 재고 기준을 입력으로 활용하여 단기 재고 소진 가능성을 시계열 기반으로 계산한다. 이 를 통해 구매 지연 또는 공급 차질 발생 시 예상되 는 재고 부족 위험을 사전에 식별한다.
Ⅳ. 시스템 구현 및 활용 결과 제안한 멀티 AI 에이전트 기반 니켈 구매 의사결 정지원시스템은 실제 구매 담당자의 판단 과정을 지원하는 것을 목표로 구현되었다. 본 장에서는 시 스템 설계 자체를 반복적으로 설명하기보다는, 사용 자가 시스템을 통해 어떤 정보를 입력하고, 그 결과 가 어떤 형태로 제공되는지를 구현 결과를 통해 설 명한다. 특히 단일 예측 값이 아닌, 복수의 분석 결 과가 통합된 의사결정 지원 화면을 중심으로 시스 템의 활용 가능성을 논의한다.
4.1 프로토타입시스템구성 구현된 시스템은 Streamlit 라이브러리를 활용한 로컬 웹 기반에서 확인할 수 있는 대시보드 형태로 제공되며, 구매 담당자가 의사결정에 필요한 조건을 입력하고 분석 결과를 직관적으로 확인할 수 있도

<!-- page 7 -->

Journal of KIIT. Vol. 24, No. 7, pp. 287-298, Jul. 31, 2026. pISSN 1598-8619, eISSN 2093-7571 293 록 설계되었다. 사용자가 입력한 재고 수준, 구매 조건, 시점 정보 등은 시스템의 공통 상태로 관리되 며, 이는 이후 분석 에이전트들의 호출 기준으로 활 용된다.
사용자 요청이 입력되면 시스템은 구매 판단에 직접적으로 필요한 분석 결과를 중심으로 화면을 구성하며, 재고 분석이나 가격 분석 등 상황에 맞는 정보만이 대시보드에 제시된다. 이 과정에서 모든 분석 결과가 일괄적으로 표시되는 것이 아니라, 현 재 의사결정 상황에 따라 핵심적인 분석 결과만이 제공되도록 설계되었다. 이러한 실행 흐름은 분석 효율성을 유지하면서도 구매 판단에 필요한 정보를 충분히 제공하도록 구성하였다.
4.2 결과화면및시각화 그림 3은 시스템의 결과 화면을 나타낸다. 해당 대시보드는 개별 에이전트의 분석 결과를 그대로 노출하는 방식이 아니라, 구매 의사결정에 직접적으 로 활용 가능한 정보만을 요약된 형태로 제공하도 록 설계되었다.
화면에는 가격 변동 방향에 대한 해석, 주요 영 향 요인 요약, 그리고 구매 판단에 참고할 수 있는 정성적 설명이 함께 제시된다. 이러한 표현 방식은 모델 내부 계산 과정이나 세부 파라미터를 직접 제 시하지 않으면서도, 사용자가 결과의 맥락을 이해할 수 있도록 돕는 데 목적이 있다.
4.3 시나리오기반사례분석 본 사례에서는 재고 수준과 입고·소비 계획이 먼 저 설정된 상황에서, 계획 에이전트가 향후 구매 시 점을 수립하고, 해당 시점을 기준으로 구매 에이전 트가 7일 뒤 니켈 가격을 예측하며, 이 결과를 바탕 으로 재고 에이전트가 재고 리스크를 분석하는 경 우를 가정하였다.
해당 상황에서 구매 판단 요청이 입력되면, 오케 스트레이션 에이전트는 재고 리스크와 예측된 가격 변동성을 핵심 판단 요소로 활용하여 재고 에이전 트와 구매 에이전트의 분석 결과를 중심으로 의사 결정 지원을 수행한다.
재고 에이전트는 재고 소진 속도와 안전 재고 기 준을 기반으로 재고 부족 가능성을 분석하며, 구매 에이전트는 가격 예측 결과와 함께 가격 변동에 영 향을 미친 주요 요인을 도출한다. 오케스트레이션 에이전트는 이들 분석 결과를 통합하여, 구매 시점 조정이 필요하다는 의사결정 지원 정보를 생성한다.
그림3. 멀티에이전트기반구매의사결정대시보드 Fig. 3. Multi-AI agent procurement decision dashboard

<!-- page 8 -->

294 멀티AI 에이전트기반니켈조달의사결정지원시스템프레임워크설계및개발 본 사례는 니켈 가격 변동성과 재고 리스크를 중 심으로 구매 시점 의사결정을 지원하는 시나리오로 설계되었다. 따라서 품질 관련 문서 입력이나 품질 이상 징후 분석은 연구 범위에서 제외하였으며, 원 자재 적합성 검토를 담당하는 품질 에이전트는 호 출 대상에 포함되지 않았다. 이러한 설계는 모든 에 이전트를 일괄적으로 실행하는 방식이 아니라, 사용 자 질의와 공통 상태 정보를 기반으로 상황에 필요 한 분석만을 선택적으로 수행하는 오케스트레이션 에이전트의 동작 원리를 반영한 것이다. 이를 통해 사용자는 정보 과부하 없이 현재 의사결정 상황에 핵심적인 재고 소진 가능성과 가격 예측 결과만을 집중적으로 검토할 수 있다.
이와 같은 분석 흐름을 통해 사용자는 단일 예측 결과에 의존하지 않고, 재고 상태와 가격 요인을 종 합적으로 고려하여 구매 판단을 수행할 수 있다. 이 는 제안한 시스템이 복수의 분석 관점을 통합하여 실제 구매 의사결정을 지원할 수 있음을 보여준다.
4.4 구매에이전트평가및분석 3.2절에서 기술한 데이터 구성 및 학습 설정을 기반으로, 구매 에이전트의 가격 예측 성능을 정량 적으로 검증하였다. 본 절에서는 앞선 사례 분석에 서 활용된 예측 결과가 실제 의사결정 지원에 활용 되기에 충분한 신뢰성을 갖는지를 확인하기 위해 모델 성능을 비교하였다.
4.4.1 모델 성능 평가 구매 에이전트의 가격 예측 성능을 검증하기 위 해 선형 회귀 계열 모델과 트리 기반 모델을 포함 한 다수의 머신러닝 모델을 비교 실험하였다. 모든 모델은 3.2절에서 정의한 학습 설정에 따라 평가되 었으며, 학습 구간에서 시계열 교차검증을 통해 하 이퍼파라미터를 조정하였다. 성능 평가는 RMSE, R², MAE, MAPE를 기준으로 확인하였으며, 모델별 성능 비교 결과는 표 2에서 확인할 수 있다.
모델 비교 결과, 트리 기반 모델보다 선형 계열 모델이 전반적으로 우수한 성능을 보였으며, 이는 대부분의 입력 변수가 연속형으로 구성된 다변량 시계열 데이터라는 특성과 관련이 있는 것으로 해 석할 수 있다. 이에 따라 Linear, Lasso, Ridge, Elastic Net과 같은 선형 기반 모델을 중심으로 추가 적인 비교를 수행하였다.
특히 표 2에서 Linear 모델은 Test RMSE, Test R², Test MAE, Test MAPE 기준에서 Ridge보다 더 우수한 성능을 보였으나, 교차검증 성능(CV RMSE) 에서는 Ridge보다 상대적으로 낮은 성능을 나타냈 다. 이는 Linear 모델이 특정 테스트 구간에 대해 상대적으로 높은 적합도를 보였을 가능성을 시사하 며, 시계열 예측 환경에서 요구되는 일반화 성능 측 면에서는 한계가 있을 수 있다.
또한 유가, 거시경제 지표 및 타 원자재 가격 등 다변량 외생 변수 간의 높은 상관관계가 존재하는 데이터 특성상, 변수를 선택적으로 제거하는 Lasso나 ElasticNet의 L1 규제보다는 모든 변수의 기여도를 보존하면서 가중치를 안정적으로 축소하는 Ridge의 L2 규제가 복합적인 시장 신호를 유지하며 다중공선 성을 완화하는 데 더욱 적합한 것으로 판단된다.
표2. ML 모델성능평가 Table 2. Performance of ML models Model CV RMSE Test RMSE Test R² Test MAE Test MAPE Linear 1057.04 665.60 0.94 481.67 2.63 Lasso 886.90 827.64 0.91 692.05 3.96 Ridge 879.57 784.30 0.92 620.42 3.47 Elastic net 908.22 797.70 0.92 634.04 3.55 RF 1776.89 1348.67 0.77 923.33 4.83 AdaBoost 1682.56 1269.87 0.80 889.05 4.67 XGBoost 1811.98 1151.32 0.83 808.16 4.29 LightGBM 1832.38 1231.67 0.81 900.61 4.85

<!-- page 9 -->

Journal of KIIT. Vol. 24, No. 7, pp. 287-298, Jul. 31, 2026. pISSN 1598-8619, eISSN 2093-7571 295 따라서 본 연구에서는 단일 테스트 성능보다는 교차검증과 테스트 성능 간의 일관성을 모델 선택 기준으로 고려하였으며, 이는 기존 연구에서 제시된 일반화 성능 중심의 모델 선택 논의에 기반한다 [17]. 이러한 기준에 따라 구매 에이전트의 가격 예 측 모델로 Ridge Regression을 활용하였다.
4.4.2 구매 에이전트 결과 기반 리랭킹 성능 평가 이후, 구매 에이전트는 예측 결과를 실무적 의사결정에 활용할 수 있도록 외부 시장 정 보를 결합한 리랭킹 과정을 수행한다. 해당 과정은 가격 예측 결과의 해석 가능성을 강화하고, 구매 판 단에 필요한 시장 맥락 정보를 함께 제공하는 것을 목적으로 한다.
먼저, SHAP(SHapley Additive exPlanations) 기반 방법론[18]을 활용하여 특정 시점의 가격 예측에 가장 큰 영향을 미친 상위 3개 변수들을 도출한다.
해당 변수들은 외부 시장 정보 탐색의 기준으로 활용된다.
이후 사용자가 선택한 기준 날짜를 중심으로 이 전 14일간의 관련 뉴스 및 시장 동향 정보가 Google Search API를 통해 수집된다. 수집된 기사들 은 SHAP 상위 변수와의 연관성을 기준으로 정제되 며, 변수와의 매핑 정도에 따라 재정렬된다.
본 연구에서는 기사 내용과 SHAP 분석을 통해 도출된 상위 3개 주요 변수와의 연관성 수준을 별 점으로 구분해 제시하였다. 기사 내용이 하나의 변 수와 매핑되는 경우에는 한 개의 별로, 두 개의 변 수와 매핑되는 경우에는 두 개의 별로, 세 개의 변 수 모두와 매핑되는 경우에는 세 개의 별로 표시하 였다. 이러한 단순화된 표현은 연속적인 유사도 점 수를 직접 제시하는 방식보다 인지적 부담을 줄이 고, 예측의 근거가 되는 시장 신호를 빠르게 파악할 수 있도록 지원한다.
그림 4는 구매 에이전트의 통합 인터페이스 화면 을 나타낸다. 해당 화면은 사용자의 질의와 이에 대 한 응답이 순차적으로 제시되는 챗봇 기반 구조로 구성되며, 예측 결과 이후에는 추가 분석 결과가 동 일 화면 내에서 대시보드 형태로 표시된다.
그림4. 구매에이전트결과화면 Fig. 4. Purchase agent interface

<!-- page 10 -->

296 멀티AI 에이전트기반니켈조달의사결정지원시스템프레임워크설계및개발 예를 들어 사용자가 7일 후 가격 예측을 요청하면, 예측 가격(15,701.68 USD)과 변동률(+2.86%)이 함께 표시된다. 이어서 원인 및 관련 뉴스 분석 요청이 이 루어질 경우, 대시보드 형태로 SHAP 분석을 통해 도 출된 상위 3개 영향 변수(PC_COM_1, PC_COM_3, PC_COM_2)와 함께 해당 변수들과 관련된 뉴스가 함 께 제공된다. 본 사례에서는 시장 동향과 관련된 기 사([LME-1013], [LME-1014])가 제시되었다.
이와 같이 구매 에이전트는 예측 결과와 함께 주 요 변수 및 관련 시장 정보를 하나의 대화 흐름 안 에서 통합적으로 제공함으로써, 사용자가 예측 결과 와 배경을 동시에 이해할 수 있도록 지원한다.
다만 뉴스 요약 관련 정보는 LLM 기반으로 수 행되므로, 생성된 정보는 단독 의사결정 기준이 아 닌 보조적 참고 정보로 활용되도록 설계하였다. 또 한 LLM 기반 생성 과정에서 발생할 수 있는 Hallucination 가능성을 고려하여 기사 제목, 날짜, 요약문 및 관련성 별점과 같은 근거 정보를 함께 제시하였으며, 단일 뉴스 요약 결과만으로 가격 변 동 원인을 단정하거나 구매 권고를 생성하지 않도 록 구성하였다.
Ⅴ. 결론 및 시사점 본 연구에서는 니켈 원자재 구매 과정에서 발생 하는 복합적인 의사결정 문제를 지원하기 위해, 멀 티 AI 에이전트 기반 의사결정지원시스템을 설계하 고 이를 기반으로 구현하였다. 시스템은 가격, 재고, 물류, 통관 등 구매 판단에 필요한 분석 기능을 역 할 기반 에이전트로 분리하고, 오케스트레이션 에이 전트를 통해 이를 통합하는 구조를 가진다.
기존 니켈 가격 예측 연구가 주로 예측 정확도 향상에 초점을 두었다면[7], 본 연구는 예측 결과를 포함한 다양한 분석 요소를 실제 구매 의사결정 맥 락 안에서 통합하는 구조적 프레임워크를 제안하였 다. 또한 인간 주도형 멀티 에이전트 연구가 조직 내 관점 조율과 합의 형성에 중점을 두었다는 점 [13]과 비교할 때, 본 연구는 정량적 예측 모델과 정성적 리스크 분석을 통합하여 공급망 리스크를 종합적으로 고려하는 의사결정지원 구조를 설계하 였다는 점에서 차별성을 가진다. 이는 단일 모델 기 반 접근이나 단순한 분석 결과 나열을 넘어, 복합 리스크 환경에서 일관된 판단 흐름을 구성하는 오 케스트레이션 기반 의사결정지원시스템 아키텍처를 제안하였다는 데 의의가 있다.
Streamlit 기반으로 구현된 시스템은 실제 외부 가격 데이터와 통관 규제 정보를 포함한 입력 데이 터를 활용하여 다수의 에이전트 실행 흐름을 구성 하고 적용 가능성을 확인하였다. 그 결과, 단일 예 측 값에 의존하기보다 복수의 분석 관점을 종합적 으로 제시하는 방식이 구매 담당자의 판단 과정을 보다 구조화하는 데 기여할 수 있음을 보여준다. 이 러한 결과는 개별 예측 모델의 성능 개선을 넘어, 의사결정 과정 전반을 설계 수준에서 지원하는 접 근의 실현 가능성을 시사한다.
본 연구는 멀티 에이전트 기반 의사결정 구조의 설계와 실행 메커니즘을 중심으로 구조적 설계의 타당성을 제시하였다. 일부 에이전트의 경우 산업 현장의 실시간 내부 데이터와 완전하게 통합된 환 경까지 확장되지는 않았으나, 해당 기능은 기업 시 스템과의 연계를 전제로 설계되었다는 점에서 향후 확장 가능성을 내포한다. 제안한 구조의 효과를 보 다 엄밀하게 검증하기 위해서는 실제 기업의 재고 시스템, 물류 이벤트 데이터, 품질 인증 문서 등과 의 직접적인 데이터 연계 기반의 정량적 평가와 사 용자 기반 실증 연구가 추가적으로 요구된다.
또한 본 연구에서 활용된 LLM 기반 리랭킹 과 정에서 오류 가능성을 완전히 배제할 수 없다는 한 계를 가지며, 향후 연구에서는 생성 정보의 신뢰성 을 보다 체계적으로 검증할 필요가 있다.
향후 연구에서는 제안한 멀티 AI 에이전트 기반 의사결정지원 구조를 니켈 원자재 구매뿐만 아니라, 다양한 원자재를 취급하고 복합적인 공급망 구조를 가진 기업 환경으로 확장하는 방안을 고려할 수 있 다. 또한 대형 언어 모델 기반 구현에 한정하지 않 고, 소형 언어 모델(SLM, Small Language Model)을 활용한 경량화된 에이전트 구성이나 기업 내부 보 안 환경에 적합한 폐쇄형 시스템 설계에 대한 탐색 역시 중요한 연구 방향이 될 수 있다. 이러한 확장 은 실제 공급망 환경에서 본 연구가 제안한 구조적 접근의 적용 범위를 더욱 구체화하는 데 기여할 것 으로 기대된다.

<!-- page 11 -->

Journal of KIIT. Vol. 24, No. 7, pp. 287-298, Jul. 31, 2026. pISSN 1598-8619, eISSN 2093-7571 297 References [1] T. E. Graedel, J. Allwood, J.-P. Birat, M. Buchert, C. Hageluken, B. K. Reck, S. F. Sibley, and G.
Sonnemann, "What Do We Know About Metal Recycling Rates?", Journal of Industrial Ecology, Vol. 15, No. 3, pp. 355-366, May 2011.
https://doi.org/10.1111/j.1530-9290.2011.00342.x.
[2] X. Zhou, S. Zheng, H. Zhang, Q. Liu, W. Xing, X. Li, Y. Han, and P. Zhao, "Risk Transmission of Trade Price Fluctuations from a Nickel Chain Perspective: Based on Systematic Risk Entropy and Granger Causality Networks", Entropy, Vol.
24, No.
9, Art.
no.
1221, Aug.
2022.
https://doi.org/10.3390/e24091221.
[3] M. Christopher and H. Peck, "Building the Resilient Supply Chain", International Journal of Logistics Management, Vol. 15, No. 2, pp. 1-13, Jul. 2004.
https://doi.org/10.1108/09574090410700275.
[4] H. Peck, "Reconciling Supply Chain Vulnerability, Risk and Supply Chain Management", International Journal of Logistics: Research and Applications, Vol.
9, No.
2, pp.
127-142, Jan.
2007.
https://doi.org/10.1080/13675560600673578.
[5] C. S. Tang, "Perspectives in Supply Chain Risk Management", International Journal of Production Economics, Vol. 103, No. 2, pp. 451-488, Oct.
2006. https://doi.org/10.1016/j.ijpe.2005.12.006.
[6] B. Lim, S. O. Arik, N. Loeff, and T. Pfister, "Temporal Fusion Transformers for Interpretable Multi-Horizon Time Series Forecasting", International Journal of Forecasting, Vol. 37, No.
4, pp. 1748-1764, Oct. 2021. https://doi.org/10.
1016/j.ijforecast.2021.03.012.
[7] T. Kim and H. Ahn, "Forecasting Nickel Commodity Prices with Liquid Neural Networks", Journal of Intelligence and Information Systems, Vol.
31, No.
3, pp.
1-24, Sep.
2025.
https://doi.org/10.13088/jiis.2025.31.3.001.
[8] P. Lewis, E. Perez, A. Piktus, F. Petroni, V.
Karpukhin, N. Goyal, H. Kuttler, M. Lewis, W.-T.
Yih, T. Rocktaschel, S. Riedel, and D. Kiela, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Advances in Neural Information Processing Systems(NeurIPS), Online, Vol. 33, pp. 9459-9474, May 2020.
https://doi.org/10.48550/arXiv.2005.11401.
[9] C. Qu, S. Dai, X. Wei, H. Cai, S. Wang, D. Yin, J. Xu, and J.-R. Wen, "Tool Learning with Large Language Models:
A Survey", Frontiers of Computer Science, Vol. 19, No. 8, Art. no.
198343, Jan. 2025. https://doi.org/10.1007/s11704- 024-40678-2.
[10] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z. Chen, J. Tang, X. Chen, Y. Lin, W.
X. Zhao, Z. Wei, and J. Wen, "A Survey on Large Language Model-Based Autonomous Agents", Frontiers of Computer Science, Vol. 18, Art. no. 186345, Mar. 2024. https://doi.org/10.1007 /s11704-024-40231-1.
[11] Y. Yue, G. Zhang, B. Liu, G. Wan, K. Wang, D. Cheng, and Y. Qi, "MasRouter: Learning to Route LLMs for Multi-Agent Systems", Proc. 63rd Annual Meeting of the Association for Computational Linguistics, Vienna, Austria, pp.
15549-15572, Jul. 2025. https://doi.org/10.18653/v1/ 2025.acl-long.757.
[12] J. H. Yang and N. H. Yoo, "A Study on the Methodology for Implementing AI-Based Multi-Agent Systems in Manufacturing Environments", Journal of Korea Institute of Information, Electronics, and Communication Technology, Vol. 18, No. 3, pp. 155-171, Jun.
2025. https://doi.org/10.17661/jkiiect.2025.18.3.155.
[13] H.
Namgung, L.
Kim, and N.
Kim, "Human-Guided Multi-Agent System for Decision Support", Journal of Intelligence and Information Systems, Vol. 31, No. 3, pp. 171-189, Sep. 2025.
https://doi.org/10.13088/jiis.2025.31.11.171.
[14] D. G. Jung and J. H. Lee, "A Study on an

<!-- page 12 -->

298 멀티AI 에이전트기반니켈조달의사결정지원시스템프레임워크설계및개발 Explainable GPT-Based Stock Investment Analysis System: Integrated Design of Retrieval-Augmented Generation and Multi-AI Agent Framework", Information Systems Review, Vol. 27, No. 3, pp.
243-266, Aug.
2025.
https://doi.org/10.14329/isr.2025.27.3.243.
[15] C. Baumeister and L. Kilian, "Forecasting the Real Price of Oil in a Changing World: A Forecast Combination Approach", Journal of Business & Economic Statistics, Vol. 33, No. 3, pp. 338-351, Aug. 2015. https://doi.org/10.1080/ 07350015.2014.949342.
[16] B. Zhang, B. H. Nguyen, and C. Sun, "Forecasting Oil Prices:
Can Large BVARs Help?", Energy Economics, Vol. 137, Art. no.
107805, Jul. 2024. https://doi.org/10.1016/j.eneco.
2024.107805.
[17] S. Arlot and A. Celisse, "A Survey of Cross-Validation Procedures for Model Selection", Statistics Surveys, Vol. 4, pp. 40-79, Mar. 2010.
https://doi.org/10.1214/09-SS054.
[18] S. M. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting Model Predictions", Advances in Neural Information Processing Systems(NeurIPS), Long Beach, California, USA, Vol.
30, pp.
4765-4774, Dec.
2017.
https://doi.org/10.48550/arXiv.1705.07874.
저자소개 김 선 오 (Seono Kim) 2019년 3월 ~ 현재 : 명지대학교 경영정보학과 학부과정 관심분야 : 의사결정지원시스템, XAI, 멀티 AI 에이전트 유 지 현 (Jihyeon Ryu) 2022년 3월 ~ 현재 : 명지대학교 경영정보학과 학부과정 관심분야 : 머신러닝, 자연어 처리, 데이터 분석, AI 권 가 영 (Gayeong Kwon) 2023년 3월 ~ 현재 : 명지대학교 경영정보학과 학부과정 관심분야 : 데이터 분석, 머신러닝, Agentic AI, 멀티 AI 에이전트 이 한 준 (Hanjun Lee) 2001년 2월 : 서울대학교 컴퓨터공학과(공학사) 2004년 2월 : 서울대학교 컴퓨터공학과(공학석사) 2016년 8월 : 고려대학교 경영학과 MIS 전공(경영학박사) 2020년 3월 ~ 현재 : 명지대학교 경영정보학과 부교수 관심분야 : 머신러닝, 자연어 처리, 정보시스템, 정보화 정책
