## Failure case

Describe the academic writing behavior that currently fails. Include a minimal input
or link to an evaluation case.

## Behavioral change

Explain the smallest rule or implementation change and why it generalizes beyond
one phrase.

## Evidence integrity

- [ ] Supplied numbers, citations, equations, uncertainty, and scope are preserved.
- [ ] No new statistic, metric, probe, experiment, or citation is reported as fact.
- [ ] Defined technical terms and venue requirements still work.
- [ ] The change does not turn a style preference into a universal prohibition.

## Validation

- [ ] Added or updated a behavioral evaluation case.
- [ ] Ran `python -m unittest discover -s tests -v`.
- [ ] Ran `python scripts/check_policy_sync.py`.
- [ ] Ran the Skill structure validator.
