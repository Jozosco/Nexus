"""TE 가격 정정 오버레이 회귀 테스트 (A-290)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ingest_te_xlsx import apply_corrections  # noqa: E402


def test_corrections_replace_drop_and_guard(tmp_path: Path) -> None:
    spec = tmp_path / "c.yaml"
    spec.write_text(
        "TE_PALM_OIL:\n"
        "  - {date: 2026-08-28, te_value: 4628, action: replace, value: 4894, label: CONFIRMED}\n"
        "  - {date: 2026-09-02, te_value: 4648, action: drop, label: INFERENCE}\n"
        "  - {date: 2026-09-03, te_value: 1, action: replace, value: 2, label: INFERENCE}\n",
        encoding="utf-8")
    df = pd.DataFrame({"price_date": pd.to_datetime(["2026-08-28", "2026-09-02", "2026-09-03"]),
                       "value": [4628.0, 4648.0, 4904.0], "open": 1.0, "high": 1.0, "low": 1.0,
                       "indicator_code": "TE_PALM_OIL", "source_name": "TE"})
    out = apply_corrections(df, spec).set_index("price_date")
    assert out.loc["2026-08-28", "value"] == 4894 and pd.isna(out.loc["2026-08-28", "open"])
    assert pd.Timestamp("2026-09-02") not in out.index                 # drop
    assert out.loc["2026-09-03", "value"] == 4904                      # 원본 값 불일치 → 적용 보류
