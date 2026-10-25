# Testing (Epic 6)

## Automated tests
```
python tests/test_planning.py
python tests/test_assistant.py
```
| Test | What it checks |
|------|----------------|
| budget scales with area and quality | Bigger / premium buildings cost more; contingency maths is right |
| timeline is continuous | Each phase starts when the previous one ends |
| asset value never below salvage | Depreciation stops at the salvage value |
| INR formatting | `1234567` -> `₹12,34,567` |
| advisory: structural crack | Appears as STOP and sorts first |
| advisory: weather rules | Heavy rain, strong wind and heat each raise an advisory |
| advisory: empty / low contingency | Friendly default; low contingency is flagged |

## Manual test checklist (run the app)
- [ ] App opens without errors; sidebar accepts the API key
- [ ] No key entered -> friendly warning (no crash)
- [ ] Safety tab: site photo -> risk, hazards, PPE shown
- [ ] Safety tab: non-construction photo (e.g. a cat) -> summary says it is not a site
- [ ] Crack tab: crack photo -> severity, causes, repair steps shown
- [ ] Budget tab: change area / floors / quality -> totals, chart, Gantt and CSV update
- [ ] Budget tab: AI insights button returns suggestions
- [ ] Weather tab: valid city -> forecast table + guidance; invalid city -> "City not found"
- [ ] Assistant tab: advisories update after running other tabs; chat answers a question; Clear chat works
- [ ] Phone-size browser window still usable

Record the date, result and any bug you found for each item in your report.
