# VERIFY — 01 foundation
Status: **draft** (commands fixed now; real output pasted by Claude in §4 after T01-15) · Naveed's 10%

## 0. Setup
```bash
cd ~/ai-soc/soc-worker
git fetch && git checkout feat/01-foundation && git pull
cd backend
uv sync --all-packages          # first time downloads packages (free; PyPI)
```

## 1. Checks (command → what you must see)
| # | Command | You must see |
|---|---|---|
| 1.1 | `make help` | one line per target: dev, test, cov, lint, fmt, typecheck, eval-dry, demo-masking, clean (+ later-feature stubs) |
| 1.2 | `make lint` | `All checks passed!` and `N files already formatted` |
| 1.3 | `make typecheck` | `Success: no issues found in N source files` |
| 1.4 | `make test` | `N passed`, 0 failed, 0 errors |
| 1.5 | `make cov` | soc_shared `TOTAL ... ≥ 90%` |
| 1.6 | `make demo-masking` | BEFORE (lab values), AFTER (only `<IP-n>`/`<USER-n>`/`<HOST-n>`), `ip_context`, map counts, `LEAK CHECK: OK` |
| 1.7 | `make eval-dry` | `not implemented until feature 02`, exit 0 |
| 1.8 | `ls ../pyproject.toml ../src 2>&1` | `No such file or directory` (root scaffold removed) |
| 1.9 | `git check-ignore -v .env; git check-ignore .env.example; echo $?` | first line shows the ignore rule; the last line prints `1` (not ignored) |
| 1.10 | GitHub → Actions → the latest run on `feat/01-foundation` | jobs `python` and `secrets` green |
| 1.11 | Read `backend/docs/LEARNING.md` §01 and `CAREER-MAP.md` row 01 | you understand every file; the talking points are true |

## 2. Edge cases to try (in `uv run python`)
```python
from soc_shared.masking import MaskMap, mask_text, is_public_ip, classify_ip
m = MaskMap()
print(mask_text("Login from 10.0.0.5 and 10.0.0.5 by LAB\\alice to lab-ws01.lab.local", m))  # same IP → same token
print(mask_text("Admin then admin", m))           # no names here → unchanged (not a DOMAIN\user, not learned)
print(mask_text("see https://attack.mitre.org/techniques/T1110/ at 12:30:45", m))   # unchanged
print(mask_text("mail alice@lab.example and 203.0.113.7:443", m))  # <EMAIL-1>, <IP-2>:443
print(is_public_ip("10.0.0.5"), is_public_ip("192.0.2.1"), is_public_ip("8.8.8.8"), is_public_ip("999.1.1.1"))
# → False False True False
print(classify_ip("172.16.4.2"))                   # → private 172.16.0.0/12
print(repr(m))                                      # counts only, no raw values
```

## 3. Break it on purpose (then undo with `git checkout -- <file>`)
| Change | Expected failure |
|---|---|
| In `masking/text.py`, skip the IPv4 pass | `test_masking.py` IPv4 cases + the property test fail |
| In `ipclass.py`, make `is_public_ip` return True for 10/8 | `test_ipclass.py::test_rfc1918_not_public` fails |
| In `models/note.py`, remove the escalate⇔condition validator | `test_triage_note.py::test_escalate_needs_condition` fails |
| Change one character of `DECLINE_MESSAGE` | `test_models.py::test_decline_message_exact` fails |
| Add a line `OPENAI_API_KEY=sk-test` to `.env.example` | `test_repo_hygiene.py` fails (and gitleaks may flag it) |
| Add `import socket; socket.create_connection(("example.com",80))` in a test | the no-network guard fails that test |

## 4. Real output captured by Claude
_(filled in T01-15)_

## 5. Naveed's verdict
_(verified / changes needed — notes)_
