# Contributing

Contributions are welcome, especially realistic examples of AI-defensive academic
writing that the current Skill handles poorly.

## A useful contribution

1. Add or describe a realistic case with the source facts and user request.
2. Define observable expected behavior without prescribing exact prose.
3. Change the narrowest instruction that fixes the demonstrated failure.
4. Check that the change does not remove valid evidence, terminology, uncertainty,
   venue requirements, or explicit user style choices.

Avoid expanding a blacklist whenever a provenance or relevance rule would handle
the same failure more generally.

## Validation

Validate the Skill structure with the `quick_validate.py` script distributed with
the Codex `skill-creator` Skill, then run the cases in [`evals/cases.md`](evals/cases.md)
as forward tests with a fresh model context.

Pull requests should explain the failure case, the behavioral change, and the cases
used for validation.
