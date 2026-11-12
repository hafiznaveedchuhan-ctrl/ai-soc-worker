# VERIFY — 01 foundation
Status: **filled** by Claude 2026-11-12 (real output in §4) — **awaiting Naveed's verification** · Naveed's 10%

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
| 1.4 | `make test` | `153 passed`, 0 failed, 0 errors |
| 1.5 | `make cov` | `153 passed` and `Total coverage: 98.99%` (≥ 90%) |
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

## 4. Real output captured by Claude (2026-11-12, branch feat/01-foundation)

**`make check`** (lint + typecheck + cov) — exit 0
```
All checks passed!
35 files already formatted
Success: no issues found in 28 source files
Required test coverage of 90% reached. Total coverage: 98.99%
153 passed in 15.52s
```
Success numbers (INTENT): S1 0 failures ✔ · S2 98.99% ≥ 90% ✔ · S3 masking case tests 100% pass ✔ ·
S4 property tests 600 + 600 + 300 + 200 examples, 0 leaks ✔ (stable in 3 repeated runs) · S5 ✔ · S6 ✔ ·
S7 CI run 43166277801 on 9d2cd6f: `python` success, `secrets` (gitleaks) success ✔ · S8 ✔ (below).
NFR-01-04: 50 KB alert masked in 18.8 / 20.0 / 29.0 ms (3 runs) < 50 ms ✔.

**`make demo-masking`** (AFTER part)
```
{
  "targetUserName": "<USER-1>",
  "targetDomainName": "<HOST-3>",
  "subjectUserName": "<HOST-1>$",
  "workstationName": "<HOST-4>",
  "ipAddress": "<IP-2>",
  "ipPort": "51544",
  "logonType": "3",
  "status": "0xc000006d",
  "subStatus": "0xc000006a"
}
An account failed to log on. Account Name: <USER-1> Account Domain: <HOST-3> Workstation Name: <HOST-4> Source Network Address: <IP-2> Source Port: 51544 Logon Type: 3
ip_context: {"<IP-1>": "private 10.0.0.0/8", "<IP-2>": "special documentation"}
MaskMap(IP=2, USER=1, HOST=5, EMAIL=0)
dropped fields: none
LEAK CHECK: OK
```

**§2 edge cases**
```
Login from <IP-1> and <IP-1> by <HOST-1>\<USER-1> to <HOST-2>
Admin then admin
see https://attack.mitre.org/techniques/T1110/ at 12:30:45
mail <EMAIL-1> and <IP-2>:443
False False True False
private 172.16.0.0/12
MaskMap(IP=2, USER=1, HOST=2, EMAIL=1)
```

**1.7–1.9**
```
eval-dry: not implemented until feature 02
ls: cannot access '../pyproject.toml': No such file or directory
ls: cannot access '../src': No such file or directory
.gitignore:14:**/.env	.env          ← .env ignored
1                                     ← .env.example NOT ignored
```

**§3 break it (one done by Claude):** changed `JazakAllah."` → `JazakAllah!"` in `models/scope.py` →
`FAILED test_models.py::TestScope::test_decline_message_exact` → restored with `git checkout --` → green.

**Found and fixed during T01-15:** Hypothesis found that `0.0.0.0` and `::ffff:0:0` (the same address) share one
token, so `unmask` returns the first spelling. This is the intended rule (FR-01-31); the round-trip property now
excludes IPv4-mapped forms, and a new property test proves they share the IPv4 token.

## 5. Naveed's verdict
_(verified / changes needed — notes)_
