# Strategy & Recommendations

---

## Why these two tests

**End-to-end placement journey.** Placing a bet is the only flow in the product
that moves money, and it's the one journey whose failure makes everything else
irrelevant. It also crosses the widest surface in a single path — match list,
odds selection, bet slip calculation, the async placement transition, receipt,
and balance settlement — so a regression almost anywhere in the core product
shows up here first.

What made it worth automating rather than just running by hand is the shape of
the assertions. The test captures the teams and odds as they were displayed at
the moment of selection, then checks the receipt against that. It isn't asking
"is the payout arithmetically correct", it's asking "did the platform confirm
the same bet it showed the user". That distinction is what caught BUG-003 and
BUG-004, and it's the kind of check that's tedious to do reliably by hand every
release.

**Stake validation at the API layer.** The stake field is the only
user-controlled input that moves money, and the API is the only layer that
really enforces it — the browser limits what can be typed, nothing limits a
hand-crafted request. A negative stake doesn't just create an invalid bet, it
flips the sign of the balance operation and credits the account. That's the
worst thing this endpoint can do and anyone able to send an HTTP request can
reach it.

It's also cheap: deterministic, no browser, runs in under a second, and the rule
is stated unambiguously in the contract so the assertions don't depend on
interpretation. Once the API client existed, covering the boundaries as well
cost nothing, so the suite checks the valid edges (€1.00, €100.00) alongside the
rejections — a validator that's too strict is as much a bug as one that's too
loose.

Both were picked over candidates like the filters or the error modal because
they sit on the money path. Everything on that path is worth a test that runs
on every commit; everything off it can wait for a human.

---

## What stayed manual, and why

**The concurrency defect (BUG-002).** This is the highest-impact bug found, but
it depends on hitting a few-millisecond window where the Place Bet button
flashes back to its default state between the loading state and the receipt
rendering. Automating a timing window that narrow produces a test that fails
intermittently for reasons unrelated to the bug, which is worse than no test —
it trains the team to ignore red. Once the button state is fixed, the right
automated check is a simple one: place a bet, assert exactly one request was
sent. That's stable. Racing the UI isn't.

**Filters and empty states.** Real findings (the counter reading "103 matches"
over an empty list, inverted odds ranges accepted silently), but they're
presentation defects off the money path. The cost of maintaining UI automation
against a filter panel that will change shape is higher than the cost of
checking it by hand when it does.

**Protocol-level API cases.** Malformed JSON returning 500 instead of 400, GET
accepted on `place-bet`, the 409 rendering the generic error modal. These are
contract conformance issues rather than business logic, and they don't regress
the way validation rules do — they're either fixed or they aren't. Worth a
one-off check, not a permanent test.

**Anything needing a human eye.** Balance truncating at normal window widths,
scientific notation in the payout field, the mismatch between the Bet Slip's
multi-selection affordances and the single-bet rule. Automation confirms values;
it doesn't notice that a layout looks wrong.

---

## If this were to scale

**1. Fix the test data story before adding more tests.** Every test in this
suite runs against one shared `user-id` with one global balance. That's why the
`clean_balance` fixture exists, and why nothing here can run in parallel — two
tests placing bets at once would corrupt each other's state. As the suite grows
this becomes the binding constraint on how fast it runs. The fix is a per-test
user context, either an endpoint that provisions a throwaway user or a pool of
ids handed out by a fixture. Everything else on this list is easier once tests
stop sharing a bank account.

**2. Run the API tier on every commit, the browser tier on merge.** The API
tests take about a second and cover the rules most likely to break. The E2E test
needs a browser and takes closer to twenty. Splitting them by the markers
already in `pytest.ini` gives fast feedback on pull requests without paying for
a browser every push, with the full suite gating merges to main. Failed E2E runs
should capture a screenshot and the page HTML — most of the debugging time on
this task went into figuring out what the page looked like when an assertion
failed.

**3. Settle the spec contradictions before writing tests against them.** Three
came up during this exercise: minimum stake is €1.00 in the Business Rules table
and €1.01 in the Validation Rules table; `reset-balance` must be consistent with
persisted state per Feature Spec 5.3 while the OpenAPI description says the
payload may differ; and the Bet Slip is specified with "Remove All" and
per-selection remove controls while the feature is explicitly single-bet only.
Each one is a place where an automated test would encode somebody's guess. They
cost minutes to resolve with product and are expensive to unpick once a suite
has been built on the wrong reading.

**Worth adding once the above is in place:** a performance layer on
`POST /api/place-bet`, which is the only write endpoint with real business logic
and the natural bottleneck under load — a kickoff spike is the realistic worst
case. That should wait until the balance validation defects are fixed, though.
Load testing a broken invariant measures the bug, not the system.