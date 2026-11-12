"""`make demo-masking` — show one lab alert before and after masking (feature 01).

The fixture holds only lab values (documentation IPs, RFC 1918, invented names), so it is
safe to print. A real alert's BEFORE view must never be printed or logged.
"""

import json
from pathlib import Path

from soc_shared.masking import MaskMap, find_unmasked_pii, mask_alert
from soc_shared.models import WazuhAlert

FIXTURE = Path(__file__).parents[1] / "packages/soc-shared/tests/fixtures/win_4625.json"


def main() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    alert = WazuhAlert.model_validate(raw)
    mask_map = MaskMap()
    masked = mask_alert(alert, mask_map)
    after = json.dumps(masked.payload, indent=2)

    print("=== BEFORE (lab fixture: win_4625.json) ===")
    print(json.dumps(raw["data"]["win"]["eventdata"], indent=2))
    print(raw["full_log"])
    print("\n=== AFTER (what an LLM would see) ===")
    print(json.dumps(masked.payload["data"]["win"]["eventdata"], indent=2))
    print(masked.payload["full_log"])
    print("\n=== ip_context ===")
    print(json.dumps(masked.ip_context, indent=2))
    print("\n=== mask map (counts only — values stay in the map) ===")
    print(mask_map)
    print("dropped fields:", masked.dropped_fields or "none")
    leaks = find_unmasked_pii(after)
    print("\nLEAK CHECK:", "OK" if not leaks else f"FAILED ({len(leaks)} unmasked values)")
    raise SystemExit(0 if not leaks else 1)


if __name__ == "__main__":
    main()
