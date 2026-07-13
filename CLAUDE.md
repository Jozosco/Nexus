# CLAUDE.md — Project Nexus
> Persistent operating rules. Loaded every session by Claude Code. **Hard limit: ≤ 120 lines.**
> Project context (goals, data, glossary, scope): → `README.md §QR`
> Module-specific rules: → `.claude/rules/*.md` (load only the file relevant to your task — see §4)

---

## §BOOT — Session Start Protocol
1. Read `README.md §QR` — confirm commodity scope (soybean oil only), goal IDs (G1/G2/G3), human gate.
2. Scan `MEMORY.md` — check for known pitfalls before starting any modeling or pipeline task.
3. Load the path-scoped rule file from §4 **only if** your task falls within that module's directory.
4. State the active task and the rule sections you are applying before writing any code.
5. If the task instruction is ambiguous: ask one focused clarifying question before executing.

---

## §1 PROJECT IDENTITY

| Field | Value |
|---|---|
| **Commodity** | Soybean oil (대두유) — crude + refined. Scope is fixed; do not extend without explicit instruction. |
| **Decision output** | Daily Buy / Hold procurement signal. AI recommends; human approves. Never execute autonomously. |
| **Goals** | G1: variable importance + alerts · G2: price band forecast · G3: Bear/Bull/Hold regime signal |
| **Data scope (Phase A)** | External pipeline data only (MEMORY D-006). Internal S&OP unavailable. G2 trains in Azure ML Studio. |
| **Environment** | No CLI inside corporate firewall. Cloud-native only: Azure ML · Snowflake · GitHub Actions. |

---

## §2 HARD CONSTRAINTS — Never Override

| Constraint | Rule |
|---|---|
| **Firewall** | Never suggest `pip install`, `brew install`, or local terminal commands. Propose Azure ML / Snowflake Snowpark / GitHub Actions alternatives. |
| **Human gate** | All Buy/Hold outputs require human approval. Use **Plan Mode** for any procurement-affecting analysis. |
| **Secrets** | Never commit credentials. Use GitHub Secrets + Azure Key Vault. Always reference `os.environ['KEY']`. |
| **Scope lock** | Do not extend to commodities other than soybean oil without explicit written instruction. |
| **Serialization** | Never use `pickle`. Use `joblib` (sklearn) or `mlflow.log_model()`. |
| **Data I/O** | Never use `openpyxl` or Excel for pipelines. Snowflake is the single source of truth. |
| **Shell access** | Never use `os.system()` or `subprocess` for data access. Use SDK connectors only. |

---

## §3 CODE RULES

### 3.1 Language
| Language | When to Use |
|---|---|
| **Python** | Default: ML models, pipelines, API integration, automation |
| **R** | Only when Python lacks equivalent: VAR (`vars`), GARCH (`rugarch`), unit root tests (`tseries`) |
| **SQL** | All Snowflake queries. CTEs over nested subqueries. Always include `LIMIT` in exploratory queries. |
| **C++ / Java** | Only after Python profiling confirms bottleneck (C++) or UDF deployment requires it (Java). Add a one-line comment justifying the switch. |

### 3.2 Style
- **Python**: PEP 8 · 100-char line limit · f-strings · type hints on all function signatures.
- **R**: tidyverse style · `<-` assignment · pipe (`|>`) for chains > 2 steps.
- No magic numbers — use named constants. Self-documenting variable names.

### 3.3 Error Messages
- **All** errors, warnings, log output → **Korean (한국어)**. External library stack traces stay in English.
```python
except ValueError as e:
    raise ValueError(f"[오류] 원자재 가격 데이터 로드 실패: {e}. 데이터 형식을 확인하세요.") from e
```

### 3.4 Commits
```
feat:     add LSTM price band module (G2)
fix:      correct T+2 FX settlement offset in pipeline
refactor: extract regime detector into src/risk/
data:     update soybean oil prices to Q1-2026
docs:     revise CLAUDE.md session protocol
```

---

## §4 PATH-SCOPED RULES INDEX
> Load **only** the file matching your current working directory. Never load all files at once.

| Working In | Load | Contains |
|---|---|---|
| `src/forecasting/` or `notebooks/` | `.claude/rules/modeling.md` | G1/G2/G3 method specs, validation protocol, baseline requirements |
| `src/pipeline/` | `.claude/rules/data_pipeline.md` | Snowflake patterns, API retry logic, schema conventions |
| Any `src/` module | `.claude/rules/libraries.md` | Approved libraries with version pins (Python + R) |
| Any test file | `.claude/rules/testing.md` | pytest, great_expectations, time-aware split protocol |

---

## §5 WISC — Context Management

| Principle | Rule |
|---|---|
| **W**rite | Append new learnings to `MEMORY.md` after each resolved blocker. Git log = long-term memory. |
| **I**solate | Spawn a subagent for data-heavy research (e.g., 10-year historical audit). Return only findings to main session. |
| **S**elect | Load only the path-scoped rule file relevant to today's task (§4). Never load all rules simultaneously. |
| **C**ompress | Run `/compact` when context exceeds ~60% capacity. Preserve active task state and last key decision. |

---

## §6 HITL — Procurement Decision Gate
> Required for any output that influences a Buy / Hold decision or touches production data.

1. **Explore** — Read current market signals + internal inventory. Read-only. No writes.
2. **Plan** — Draft execution plan in Plan Mode. Explicitly state assumptions and data sources.
3. **Validate** — Human reviewer (or invoke `/co-validate` skill) checks plan for hallucinations and risk.
4. **Execute** — Implement only after explicit approval. Open a PR with a descriptive commit message.

---

## §7 MEMORY

| File | Rule |
|---|---|
| `MEMORY.md` | Append learnings and resolved blockers. Never overwrite. Read at §BOOT step 2. 최근(당월~직전월)만 유지. |
| `docs/memory_archive/YYYY-MM.md` | 월별 아카이브(내용 무변경). 필요 시 온디맨드 로드 — 아래 @import 참조. |
| `git log --oneline -20` | Run to reconstruct prior decisions before starting a task with no recent MEMORY.md entry. |

> **컨텍스트 최적화(JIT · pointer-not-copy)**: 오래된 학습은 아카이브로 이관하고 포인터만 유지.
> 과거 세부가 필요할 때만 로드: @docs/memory_archive/2026-04.md · @docs/memory_archive/2026-05.md
