# VERIFY — 11 live-eval
Filled by Claude on 2026-11-12, session 2, with the real output below. **Naveed verifies.** Nothing paid was run: $0.00 was spent.

## 1. Checks (`cd backend && make check`)
```
All checks passed!                                   (ruff)
Success: no issues found in 108 source files         (mypy)
Required test coverage of 90% reached. Total coverage: 93.43%
330 passed, 2 warnings in 22.15s                      (was 307 → +23 new: test_pipeline 6, test_live 17)
```
- `live.py` and `estimate.py` are at 100% coverage.
- `pipeline.py` is at 95%.
- `build_live` is `# pragma: no cover`: it is the PAID path, so it is not run in tests.
- The 2 warnings come from pytest-socket blocking a socket in the "handbook down" pre-flight test. This is expected: the tests cannot reach the network at all.

## 2. Requirements → proof
| FR | Proof |
|---|---|
| 01 guards | `test_paid_refuses_without_both_guards` (4 cases). In these tests `build_live` is replaced by a function that fails the test if it is ever reached. |
| 02 alerts | `test_alert_through_real_triage_flow_is_masked_and_never_approves`: the approval is asked once and rejected (spy); the context.csv text reaches the model; the output is masked. |
| 03 probes | `test_probes_through_real_ask_flow`: KSOR, rule decline (0 calls), classifier decline, web research, fresh session per probe. |
| 04 mapping | `test_non_ok_statuses_become_item_errors` (4 statuses); `test_ok_without_note_is_an_error`. |
| 05 cap | `test_run_wide_cap_stops_and_keeps_partial_results`; `test_finish_paid_full_run_and_cap_note`. |
| 06 selection | `test_only_ids_and_limit`; `test_subset_scores_only_what_ran`. |
| 07 estimate | `test_estimate_is_free_and_under_the_cap` and the output in §3. |
| 08 pre-flight | `test_preflight_up_and_down`; `test_paid_refuses_when_the_handbook_is_down`. |
| 09 outputs | `test_paid_end_to_end_offline`: JSONL and `*-paid-pilot-report.md` with "partial: 1/135 items". |
| 10 traces | `set_trace_processors([])` unless `--export-traces` (`cli.cmd_paid`). |
| 11 deps | `live.build_live`; ADR-0010. |

## 3. `make eval-estimate` (free)
```
Cost estimate — full paid run, model gpt-5-nano ($0.05/1M in, $0.4/1M out)
item                         n  tok in/item  tok out/item  expected $  pessim. $
alerts (/triage)            40       25,836        10,300      0.2165     0.5461
probes allowed (/ask)       55        8,183         3,800      0.1061     0.2733
probes declined (/ask)      40        1,064           500      0.0101     0.0261
TOTAL                                                          0.3327     0.8455
```

## 4. Other runs
- `make eval-dry` → `datasets: 135/135 = 100.0% valid`; `oracle targets: all PASS`.
- `make eval` without CONFIRM → `refused: a paid run needs --yes-paid AND CONFIRM=haan`; nothing was called.

## 5. Not done here (needs Naveed)
- `make eval-pilot CONFIRM=haan` costs about $0.02, with a cap of $0.10. The pilot covers:
  - alerts EV-A003 and EV-A034;
  - probes EV-P001 (DECLINE), EV-P021 (research), EV-P056 (KSOR) and EV-P086 (non-cyber).
  
  It needs the handbook running.
- Full `make eval CONFIRM=haan` (R5): after the pilot and the label review.

## 6. Incident
At checkpoint 2, the merged-branch guard printed PR #13 as MERGED, but the `&&` chain still pushed, because `gh` exits 0.
- **What happened:** one commit (`a77d041`) landed on the merged branch `feat/11-live-eval`. Nothing was lost.
- **Recovery:** the new branch `feat/11-live-eval-wiring` was made from `origin/main` and the commit was cherry-picked (`b56fe9c`).
- **Fix:** the guard is now `test -z "$(gh pr list --head <b> --state merged)"` (LEARNING §14).
- **Naveed's choice:** the stale remote branch `feat/11-live-eval` can be deleted.
