# PHR-0006 — Feature 01 verified; the PR merge error fixed; incident: pushed after a merged PR
- Date: 2026-11-12T06:30Z · Session: 1 · Stage: verify → fix
- Feature: 01 · Branch: feat/01-foundation · Model: claude-opus-5-5

## Prompt (verbatim)
"verify but github merge wala link ma click kya tha to kuch error ha ,usko thk kro"

## Response summary
Investigated with `gh`. Two findings:
1. **Merge error cause:** PR #2 was opened as a **draft**, and GitHub cannot merge a draft PR. Fixed with `gh pr ready 2`. The PR is CLEAN, mergeable and has green checks; main is not protected.
2. **Incident (Claude's mistake):** PR #1 from the same branch had already been merged at 05:56:20Z, holding 284b865 and df7976b.
   Claude then pushed 5 more commits to the merged branch without checking, which CLAUDE.md forbids. No work was lost:
   the 5 commits (25d81b8, b8d54c9, 9d2cd6f, 749a610, 4f27426) are all in PR #2, which merges cleanly onto main.
   Prevention: CLAUDE.md now requires `gh pr list --head <branch> --state merged` to be empty before every push, and says to open PRs as ready, not draft.

## Files touched
CLAUDE.md, progress.md, specs/01-foundation/VERIFY.md (verdict: verified), history/prompts/{README,PHR-0006}.md

## Decisions / outcomes
Feature 01 = verified. The pre-push guard is now a rule.

## Follow-ups
Naveed: merge PR #2. Claude: feature 02 on a new branch `feat/02-evals-first` from the updated main.
