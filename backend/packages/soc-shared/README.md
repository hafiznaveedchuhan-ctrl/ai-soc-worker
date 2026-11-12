# soc-shared

Shared library for every soc-worker service: **data contracts**, the **masking engine**, and a
**settings base**. Pure Python, no network. Backend part: shared code (not a service, no image).

## Public API
```python
from soc_shared.models import (
    WazuhAlert,
    MaskedAlert,
    KsorHit,
    TriageNote,
    Verdict,
    Severity,
    Evidence,
    WebSource,
    IpReputation,
    AskAnswer,
    ScopeVerdict,
    DECLINE_MESSAGE,
    Decision,
    AuditEvent,
    LlmUsage,
)
from soc_shared.masking import (
    MaskMap,
    Kind,
    mask_alert,
    mask_text,
    unmask,
    find_leaks,
    find_unmasked_pii,
    classify_ip,
    is_public_ip,
)
from soc_shared.settings import BaseServiceSettings
```

## Example
```python
from soc_shared.masking import MaskMap, mask_text, unmask

m = MaskMap()
masked = mask_text(r"LAB\alice from 10.0.0.5", m)  # '<HOST-1>\<USER-1> from <IP-1>'
unmask(masked, m)  # back to the original (api-gateway only)
```

## Run its tests (from `backend/`)
`make test` · `make cov` · `make typecheck` · `make demo-masking`

## Environment variables
None of its own. `BaseServiceSettings` reads `<PREFIX>_ENV`, `<PREFIX>_LOG_LEVEL`,
`<PREFIX>_TRACE_INCLUDE_SENSITIVE_DATA` for each service's prefix.

Details: `../../docs/LEARNING.md` §3–5 · spec: `../../../specs/01-foundation/spec.md`.
