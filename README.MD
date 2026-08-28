# Sporty Group — QA Engineer Take-Home Assignment

This repository contains my submission for the Senior QA Engineer technical
assignment: a sports betting web application simulating a single bet
placement flow.

## Contents

- **`test_plan.md`** — Test plan with 5–6 prioritized scenarios, covering
  happy paths, negative/validation cases, and boundary conditions.
- **`execution_results.md`** — Execution results for the top 3 priority
  scenarios, plus bug reports for the issues found during testing.
- **`automation/`** — Automation framework (Python, Selenium + Pytest, API
  tests via `requests`), with one E2E UI test and one API test.
- **`strategy.md`** — Strategy and recommendations note: rationale for what
  was automated, what was left manual, and recommendations if the project
  were to scale.

## Application under test

- **URL:** `https://qae-assignment-tau.vercel.app`
- **API docs:** `/api/docs` (Swagger UI)

## How to navigate this repo

Start with `test_plan.md` for the testing approach, then `execution_results.md`
for what was found. `automation/` has its own README with setup and run
instructions for the automated suite. `strategy.md` ties it together with the
reasoning behind the automation choices and recommendations for scaling.

---

*This README will be expanded once the automation framework is finalized.*