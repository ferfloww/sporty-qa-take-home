# Sports Betting — Test Automation

Automated coverage for the Single Bet Placement feature: one end-to-end UI
journey and one API validation suite.

---

## Setup

Needs Python 3.9+ and Chrome. Selenium 4 handles the driver itself, so there's
no ChromeDriver to install.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
pytest                  # everything
pytest -m api           # API only, no browser, runs in seconds
pytest -m e2e           # the browser journey
pytest -m critical      # critical business rules across both
```

Runs with a visible, maximized Chrome window — the `driver` fixture in
`conftest.py` doesn't wire up headless mode yet, so add that before running
the e2e suite in CI.

Environment and user are configurable — either inline or via a `.env` file
(copy `.env.example`, it's picked up automatically):

```bash
BASE_URL=https://staging.example.com USER_ID=some-other-user pytest
```

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` | App and API host |
| `USER_ID` | `candidate-2zwV7d2uMnKk` | Test account |
| `API_TIMEOUT` | `10` | Seconds, HTTP request timeout |
| `EXPLICIT_WAIT` | `10` | Seconds, Selenium wait timeout |

### Allure report

```bash
pip install allure-pytest        # already in requirements.txt
pytest --alluredir=allure-results
allure serve allure-results      # needs the allure commandline, e.g. `brew install allure`
```

Failed browser tests attach a screenshot and the page HTML at the point of
failure (see the `driver` fixture in `conftest.py`), so a red e2e run in the
report shows what the page actually looked like instead of just a stack
trace.

---

## Structure

```
automation/
├── config.py                        env settings + business rule constants
├── conftest.py                      driver, api client, balance reset fixtures
├── utils.py                         parse_number, shared by pages and components
├── pytest.ini                       markers and run defaults
├── api/
│   ├── http_client.py               generic GET/POST wrapper over requests
│   └── betting_client.py            the four betting endpoints
├── pages/
│   ├── base_page.py                 waits and element interactions
│   ├── home_page.py                 the app is a single screen, this is it
│   ├── models.py                    MatchSelection, BetSlipInfo, Receipt
│   └── components/
│       ├── match_list.py            the match catalogue and its cards (MatchList, MatchCard)
│       ├── bet_slip.py              selection, stake, place bet
│       └── receipt_modal.py         the modal after placement
└── tests/
    ├── test_place_bet_e2e.py        placement journey end to end
    └── test_stake_validation_api.py stake rules at the API layer
```

The app is a single page, so there's one `HomePage` that owns the components
rather than several page objects pretending to be separate screens. Components
find their own elements and hand back the data models in `models.py`, so tests
never touch a locator.

---

## Notes on a few decisions

**No sleeps.** Everything goes through explicit waits, and `place_bet()` blocks
until the flow lands on either the receipt or the error modal. Placement is
genuinely async and sleeping through it is slower and flakier than waiting on
the actual condition.

**State gets reset, not assumed.** Placing a bet changes the balance, so tests
that care about it take the `clean_balance` fixture. It resets and then reads
the value back with `GET /api/balance` — the reset response and the persisted
balance don't agree (BUG-005), and the persisted one is what actually gets
enforced.

**Match ids come from the API.** `get_first_match_id()` pulls a real id at
runtime instead of hardcoding one, so the suite doesn't break when the fixture
data changes.

**Selection state is captured before clicking.** `select_odd_type()` reads the
teams and odds off the card and returns them, so the receipt can be checked
against what the user actually saw rather than a hardcoded value. That's what
makes the test able to catch a receipt that contradicts the bet, not just one
that's arithmetically wrong.

**Locators use ids where the app provides them** (`bet-slip-place-bet`,
`odds-...-home`, `modal-success-payout`) and fall back to semantic classes
otherwise. The one exception is telling a match card's home team from its
away team, which relies on DOM order (`:nth-of-type`) since the app doesn't
tag either one individually.

---

## Expected failures

The assertions follow the Feature Spec and the OpenAPI contract, so some of
them fail against the current build. That's intended.

| Test | Fails on | Defect |
|------|----------|--------|
| `test_negative_stake_is_rejected` | Negative stake accepted, balance credited | BUG-001 |
| `test_boundary_stake_is_accepted` | `currency` comes back as `USD` instead of `EUR` | BUG-001 |
| `test_place_bet_end_to_end` | Receipt swaps home/away teams and shows a payout that differs from the confirmed value | BUG-003, BUG-004 |

Rewriting these to accept the current behaviour would mean a green suite over a
product that misstates what a user stands to win and lets an account credit
itself. They're written to hold the spec and go green when the bugs are fixed.

One value worth flagging rather than failing: `BusinessRules.STAKE_MIN` is set
to `1.00`, matching the OpenAPI schema (`stake.minimum: 1`) and the error
message the API returns. Feature Spec section 3 also says €1.00, but section
4.1 says €1.01. The suite asserts the contract; the discrepancy is raised in
the strategy note.