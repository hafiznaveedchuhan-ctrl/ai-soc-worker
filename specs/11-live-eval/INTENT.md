# INTENT — 11 live-eval (R4)
Owner: Naveed (session 2, 2026-11-12, PHR-0014). The plan was approved with the defaults Q1–Q3 (PHR-0015).

> "R4 shuru karo: soc_evals paid ko live pipeline (agent_service.flows) se jodo, naye branch feat/11-live-eval par,
> pehle ScriptedModel ke saath offline test karo, aur real run se pehle cost estimate do. Koi bhi paid ya live call
> meri 'haan' ke baghair nahi."

**Goal.** `make eval` runs the 40 alerts and the 95 probes through the real flows. It then scores them and writes
`evals/reports/<date>-paid-report.md`.

**Out of scope.** Running the paid eval itself: that is R5, which needs a separate "haan".
