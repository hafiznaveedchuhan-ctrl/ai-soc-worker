# PHR-0009 — "all haan": Wazuh ruleset read + OTRF download → 40 alerts; detection gap; VERIFY filled
- Date: 2026-11-12T07:20Z–07:40Z · Session: 1 · Stage: implement → verify
- Feature: 02 · Branch: feat/02-evals-part2 → feat/02-evals-part3 · Model: claude-opus-5-5

## Prompt (verbatim)
"all haan"

## Response summary
- Took it as "haan" to Q1 (OTRF download) and Q2 (Wazuh ruleset read). PR rhythm: "haan" does not choose (a) or (b), so (a) was taken as the default.
  Naveed's real rhythm then turned out to be (b): he merged PR #4 minutes after the push. Adapted: a new branch per push, and the memory was updated.
  Label verification is NOT implied: labels stay UNVERIFIED.
- **Q2:** downloaded the ruleset XML for v4.14.10 into the scratchpad. Found the rules and recorded file:line:
  - 4151 (firewall drops, port scan);
  - 91809 (PowerShell Base64) and 91844 (Run key, level 12);
  - 92068 (PsExec child process);
  - 92900 (LSASS access only for masks 0x1010/0x40).
- **Q1:** downloaded 6 OTRF datasets into a separate scratchpad folder and parsed them with `python3 -I` (untrusted data). Picked the events that the default
  ruleset really alerts on: PsExec 7045, `reg save` of LSA secrets under PSEXESVC, the 4624/4672 logon of pgustavo, the Covenant remote service 7045,
  and the FIM file add of the dumped hive.
  The other 4 datasets (CMSTP, bitsadmin, comsvcs and Dumpert LSASS dumps) raise no default alert. They were recorded as a detection gap instead of being faked.
- The invented-MITRE check caught Claude's own label mistake (EV-A036). Fixed the playbook count (10, not 11).
- Wrote: ADR-0009 Accepted, THIRD_PARTY_NOTICES.md (MIT text verified identical), LEARNING §8, CAREER-MAP row 02, evals README, VERIFY §4 with real output.

## Files touched
backend/evals/scripts/build_alerts.py, data/{alerts/EV-A031…A040.json, labels.csv, context.csv, THIRD_PARTY_NOTICES.md}, recordings, review sheet,
tests, report.py; backend/docs/{adr/ADR-0009, adr/README, LEARNING, CAREER-MAP}.md; specs/02-evals-first/{INTENT,spec,plan,tasks,VERIFY}.md; progress.md.

## Decisions / outcomes
40 alerts, 95 probes, eval-dry oracle passes every target, 204 tests pass. No raw OTRF or Wazuh file is committed (only derived alerts plus the notices).

## Follow-ups
Naveed: verify feature 02 and review the labels (the NOTE items are in VERIFY §4). Claude: feature 03 docs after that.
