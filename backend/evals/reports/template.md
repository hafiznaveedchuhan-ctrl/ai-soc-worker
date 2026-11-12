# Eval report — $mode run, $date

| Run | |
|---|---|
| Mode | $mode |
| Git commit | $git_sha |
| Prediction source | $source |
| Models | $models |
| Dataset | $dataset_sizes |
| Labels verified by Naveed | $verified |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
$targets_table

## Triage (alerts)
$triage_table

### Confusion matrix (rows = label, columns = prediction)
$confusion_table

## Scope (probes)
$scope_table

## Cost and latency
$cost_table

## Failures ($failure_count)
$failures_table

## Known dataset notes
$notes
