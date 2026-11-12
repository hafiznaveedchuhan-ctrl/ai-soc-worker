# soc-evals

Labelled eval datasets, scorer and reports for the soc-worker agents (feature 02, evals-first).
Backend part: **quality gate** (not a service, no image). Spec: `../../specs/02-evals-first/`.

```bash
make eval-dry          # free, offline: validate datasets + score recorded predictions → reports/<date>-dry-report.md
make eval-stats        # dataset composition and how many labels Naveed verified
make eval-review       # review/labels-review.md — the sheet Naveed uses to verify labels
make eval-recordings   # rebuild alerts, labels, probes and the dry recordings from scripts/
make eval              # PAID run — refuses until features 05/06 + Naveed's "haan"
```

Data: 40 alerts (34 SYNTHETIC lab, 6 OTRF-derived), 95 probes. All labels are **UNVERIFIED** until `verified_by` is filled.
Attribution: `data/THIRD_PARTY_NOTICES.md` (OTRF Security-Datasets, MIT; Wazuh ruleset v4.14.10 rule lines read).
No environment variables. Explained in `../docs/LEARNING.md` §8.
