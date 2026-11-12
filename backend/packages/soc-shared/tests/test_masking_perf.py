"""NFR-01-04 — masking a ~50 KB alert stays fast (generous budget to avoid flaky CI)."""

import time
from typing import Any

from soc_shared.masking import MaskMap, mask_alert
from soc_shared.models import WazuhAlert

BUDGET_SECONDS = 0.25  # target is < 50 ms on the dev machine; CI runners are slower


def test_50kb_alert(win_4625: dict[str, Any]) -> None:
    line = "Failed logon for alice from 203.0.113.45 on lab-ws01.lab.local. "
    win_4625["full_log"] = line * (50_000 // len(line))
    alert = WazuhAlert.model_validate(win_4625)
    start = time.perf_counter()
    out = mask_alert(alert, MaskMap())
    elapsed = time.perf_counter() - start
    print(f"mask_alert 50KB: {elapsed * 1000:.1f} ms")
    assert elapsed < BUDGET_SECONDS
    assert "alice" not in out.payload["full_log"]
