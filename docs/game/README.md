# Case-file game

[Root README](../../README.md) is canonical. Run `python app.py` and open http://127.0.0.1:8765/game, or print the generated files under `game/v1/print` and `game/v1/ledgers`. Every identity, event, and value is fictional.

## Play without code

Print one case page and matching ledger per player or team, plus one score sheet. Keep `game/v1/instructor/answers.json` with the facilitator. The generated [rules](../../game/v1/rules.md) support two modes:

- **Cooperative:** discuss one shared submission and agree on the next evidence request.
- **Competitive:** submit independently; points rank the round, and fewer unsupported findings break ties.

The four cases cover same-day round totals, a small suspicious number pattern, confirmations that exceed a complete fictional tape by 0.8%, and missing authorization references concentrated in one fictional branch. Each ledger has 16 rows and one intended group-level finding among several plausible review choices.

## Score

Each correct scoped candidate has case points. Add 20 points for finding all designed targets and up to 20 for speed. Subtract 15 for every unsupported candidate; clamp the total at zero. The UI sends selected candidate IDs and elapsed seconds to the loopback server, then reveals the facilitator rationale. Scores saved for comparison stay only in browser storage and can be cleared in the UI.

Points are game mechanics. They do not represent criminality, damages, victim loss, fraud probability, or the relative importance of real cases. The strongest play identifies the narrow contradiction and asks for corroborating evidence without naming a culprit.

## Analyst extension

The round-total, number-pattern, and market-capacity cases link to the matching forensic-practicum lessons, where the learner can use Python, R, or Power BI on larger fixtures. The authorization case links to the sourced Wells Fargo guide while keeping its own records entirely fictional. The public outcome is historical context, not a source for the game ledger.

## Build and verify

```powershell
python game_fixture.py build
python game_fixture.py verify
python -m unittest tests.test_game tests.test_app
python scripts/check_browser.py
```

`build` writes 17 deterministic artifacts: public catalog, four player JSON files, four CSV ledgers, four Markdown print pages, facilitator answers, rules, score sheet, and manifest. `verify` compares committed bytes. The browser test covers answer separation before submission, perfect scoring, local results, the advanced case, and mobile width.

## Common issues

- **404 at `/game`:** stop the old Python process and restart `python app.py`; the server does not hot-reload.
- **Answer visible before play:** distribute only `print/`, `ledgers/`, rules, and blank score sheets. The open-source facilitator key is intentionally separate, not secret.
- **Table does not fit:** use portrait Letter at 100% or the browser print command from the selected case. Long labels may fit better at 90%.
- **A player selects a row as fraudulent:** score only the candidate group and ask what independent source could identify a false row. The packet does not support a person-level accusation.
- **Tied competitive score:** fewer unsupported candidates wins; if still tied, lower elapsed time wins.
