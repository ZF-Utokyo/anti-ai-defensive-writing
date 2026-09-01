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

If the Skill removed legitimate academic content, use the dedicated
[false-positive issue form](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/issues/new?template=false-positive.yml).
Include the smallest public excerpt, its academic context, and the fact, definition,
venue rule, or author preference that should protect it.

## Validation

Run:

```bash
node --test tests/test_installer.mjs
python3 -m unittest discover -s tests -v
python3 scripts/check_policy_sync.py
npm pack --dry-run
```

Validate the Skill structure with the `quick_validate.py` script distributed with
the Codex `skill-creator` Skill, then run relevant cases in
[`evals/cases.md`](evals/cases.md) as forward tests with a fresh model context.

Pull requests should explain the failure case, the behavioral change, and the cases
used for validation.
