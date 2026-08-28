# Test Plan — Single Bet Placement Feature
## Sporty Group QA Take-Home Assignment | Part A.1

### Scope and prioritisation approach

This plan covers the Single Bet Placement feature as defined in the Feature Specification. Scenarios are prioritised by **financial risk**: defects that allow incorrect money movement, or that misrepresent money to the user, rank above defects that degrade usability or filtering.

The set spans happy path (TC-001), boundary conditions (TC-002), negative and validation cases (TC-003, TC-004), data consistency (TC-005), and concurrency (TC-006). Validation rules are exercised at both UI and API layers where Feature Spec 4.1 marks them as `UI + API`, since a rule enforced on only one layer is effectively unenforced.

---

## TC-001 — Successful single bet placement, end to end
- **Priority:** Critical
- **Risk Rationale:** This is the core revenue-generating flow of the platform. If a user cannot place a bet successfully, no other defect matters. Beyond confirming the flow completes, this scenario verifies that the money values presented to the user stay consistent from selection through to confirmation, and that the balance is correctly debited.

### Steps
1. Navigate to the application with a valid `user-id` query parameter
2. Note the balance displayed in the header
3. Select a match and click one of the odds buttons (`1`, `X`, or `2`)
4. Verify the Bet Slip shows the selected match, outcome, and odds
5. Enter a valid stake (e.g. `10.00`)
6. Verify the Bet Slip shows Total Stake and Potential Payout as `stake × odds`
7. Click "Place Bet"
8. Verify the button enters the `Placing...` loading state
9. Verify the success receipt modal appears
10. Close the receipt modal
11. Verify the header balance equals the initial balance minus the stake
12. Verify the Bet Slip returns to its empty state

### Expected Result
- The bet is placed and the success receipt modal is displayed
- The receipt contains Bet ID, match details, selection, stake, odds at placement, potential payout, and placement timestamp (Feature Spec 2.4)
- The balance is debited by exactly the stake amount
- Closing the receipt returns the user to the main flow with no active selection

---

## TC-002 — Stake boundary validation on UI and API
- **Priority:** Critical
- **Risk Rationale:** Stake limits are the primary financial control on the bet placement flow. Boundary values are where off-by-one errors concentrate, and Feature Spec 4.1 requires enforcement at both layers — an API that accepts what the UI blocks is exploitable by anyone bypassing the browser. This scenario tests the four values immediately around each limit.

### Steps

**UI layer:**
1. Select a match and open the Bet Slip
2. Enter `0.99` → observe validation feedback and the state of the "Place Bet" button
3. Enter `1.00` → observe validation feedback and button state
4. Enter `100.00` → observe validation feedback and button state
5. Enter `100.01` → observe validation feedback and button state

**API layer:**
6. `POST /api/place-bet` with `stake: 0.99` and an otherwise valid payload
7. `POST /api/place-bet` with `stake: 1.00`
8. `POST /api/place-bet` with `stake: 100.00`
9. `POST /api/place-bet` with `stake: 100.01`

*(Reset the balance via `POST /api/reset-balance` between accepted placements to isolate each case.)*

### Expected Result
- `0.99` — rejected on both layers. UI shows the minimum stake message and disables "Place Bet"; API returns `422` / `invalid_stake_min`
- `1.00` — accepted on both layers
- `100.00` — accepted on both layers
- `100.01` — rejected on both layers. UI shows the maximum stake message and disables "Place Bet"; API returns `422` / `invalid_stake_max`

> **Note:** Feature Spec section 3 (Business Rules) states a minimum stake of €1.00, while section 4.1 (Validation Rules) states €1.01. This scenario asserts against €1.00, matching the OpenAPI contract (`minimum: 1`) and the documented error message. The discrepancy is raised in the strategy note as a required specification clarification.

---

## TC-003 — Negative stake values are rejected by the API
- **Priority:** Critical
- **Risk Rationale:** The UI constrains stake input, so the API is the only layer that protects against a hand-crafted request. A negative stake inverts the sign of the balance operation, and if unvalidated would let a user credit their own account instead of debiting it. This is the highest-severity failure mode available on this endpoint, and it is reachable by anyone able to send an HTTP request.

### Steps
1. `GET /api/balance` and record the current balance
2. `POST /api/place-bet` with `{"matchId": "<valid>", "selection": "HOME", "stake": -10}`
3. Record the response status, body, and the `balance` field
4. `GET /api/balance` and compare against the balance recorded in step 1
5. Repeat steps 2–4 twice more, recording the balance progression
6. Repeat with a large negative value (e.g. `stake: -1000000`) to confirm behaviour is not magnitude-dependent

### Expected Result
- Every request returns `422` with `error: "invalid_stake_min"` and the message `"Stake must be at least 1.00."`
- The balance is unchanged across all requests
- No bet is created
- `currency` in any response remains `"EUR"` per the contract

---

## TC-004 — Stake exceeding the available balance is rejected
- **Priority:** High
- **Risk Rationale:** Feature Spec 4.1 requires that a stake must not exceed the available balance, enforced on both UI and API. This is the control that prevents a user from wagering money they do not hold. It is distinct from the static maximum (TC-002) because the limit is dynamic — it depends on the account state at the moment of placement, which makes it a common source of stale-state defects.

### Steps
1. `POST /api/reset-balance`, then `GET /api/balance` to establish the true starting balance
2. In the UI, select a match and enter a stake greater than the available balance but within the €1.00–€100.00 range (e.g. balance €50, stake `80.00`)
3. Observe the validation feedback and the state of the "Place Bet" button
4. `POST /api/place-bet` directly with the same over-balance stake
5. Record the response status and body
6. `GET /api/balance` to confirm the balance is unchanged

### Expected Result
- UI displays the insufficient balance message (Feature Spec 4.4) and disables "Place Bet"
- API rejects the request with a `422` semantic validation error
- The balance is unchanged and no bet is created
- The balance never reaches a negative value

---

## TC-005 — Receipt data is consistent with the confirmed bet
- **Priority:** Critical
- **Risk Rationale:** The receipt is the user's record of what they agreed to. Feature Spec 2.4 requires that all receipt values are consistent with what was shown before placement, and Feature Spec 2.6 requires that home/away ordering carries through to the receipt. A receipt that misstates the payout or inverts the teams means the user cannot verify what they actually bet on — which is both a trust failure and a dispute liability, since no other record of the bet is surfaced to them.

### Steps
1. Select a match, noting the exact home and away team names and their display order in the match list
2. Select the `X` (Draw) outcome and record the odds value shown
3. Enter a stake of `2.00`
4. Record the Potential Payout shown in the Bet Slip before placing
5. Click "Place Bet" and capture the `place-bet` response body from browser DevTools
6. Compare the receipt modal against three sources: the pre-placement Bet Slip, the API response, and the original match list entry
7. Verify each receipt field: match name and team order, selection, stake, odds at placement, potential payout, timestamp

### Expected Result
- Potential Payout on the receipt equals `stake × odds` and matches both the Bet Slip value and the `payout` field in the API response
- Team order on the receipt matches the match list, with the home team listed first (Feature Spec 2.6)
- Selection, stake, and odds on the receipt match the API response exactly
- The Bet ID shown is a value that originates from the backend and could be used to identify this bet

---

## TC-006 — Concurrent placement does not exceed the available balance
- **Priority:** High
- **Risk Rationale:** Users double-click, and network latency widens the window between submission and confirmation. The API contract defines a `409 bet_in_progress` response, which indicates a per-user lock is intended. This scenario verifies that the lock actually holds under realistic UI interaction, since a gap between the visual loading state and the effective lock would let duplicate placements through and push the balance below zero.

### Steps
1. `POST /api/reset-balance`, then `GET /api/balance` to establish the true starting balance
2. Open browser DevTools and select the Network tab, filtered to XHR/Fetch
3. Select a match and enter a stake equal to the full available balance
4. Click "Place Bet" and continue clicking rapidly for one to two seconds
5. Record every `place-bet` request and its response status
6. Once all requests resolve, `GET /api/balance` and record the final balance
7. Observe how many modals are rendered and what messaging each displays

### Expected Result
- Exactly one request returns `200` and results in a placed bet
- All further concurrent requests return `409` with `error: "bet_in_progress"`
- The final balance equals the starting balance minus one stake, and is never negative
- A single error modal is displayed, with messaging specific to a bet already in progress rather than the generic failure copy
- The "Place Bet" control remains non-interactive from the moment of the first click until the receipt modal is fully rendered

---

## Coverage summary

| ID | Title | Priority | Type | Layer |
|----|-------|----------|------|-------|
| TC-001 | Successful single bet placement, end to end | Critical | Happy path | UI + API |
| TC-002 | Stake boundary validation on UI and API | Critical | Boundary | UI + API |
| TC-003 | Negative stake values are rejected by the API | Critical | Negative / Security | API |
| TC-004 | Stake exceeding the available balance is rejected | High | Negative / Validation | UI + API |
| TC-005 | Receipt data is consistent with the confirmed bet | Critical | Data consistency | UI + API |
| TC-006 | Concurrent placement does not exceed available balance | High | Concurrency | UI + API |

**Not covered in this plan, by design:** filter behaviour (date and odds range), error modal recovery paths, and balance reset utility behaviour. These carry lower financial risk than the placement flow and are addressed through exploratory testing, with findings documented in the execution report.