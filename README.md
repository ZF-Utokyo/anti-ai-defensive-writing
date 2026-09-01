# Anti AI-Defensive Writing Skill

An English, zero-dependency AI skill for removing unrequested caveats, faux rigor,
opaque abstraction, and formatting residue from academic writing without weakening
claims that the evidence supports.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Test](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/actions/workflows/test.yml/badge.svg)](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/actions/workflows/test.yml)

## The problem

AI writing tools often try to sound rigorous by adding things the author never
asked for:

- reflexive caveats such as "while promising" and "we cannot claim";
- invented confidence intervals, significance tests, margins, probes, or composite
  metrics;
- gratuitous em dashes, italics, bold text, parentheses, and table decorations;
- abstract noun chains that hide the actual method or result;
- claims weakened below what the supplied evidence supports.

This is AI-defensive writing: prose shaped around hypothetical reviewer objections
instead of clear communication of the available evidence.

## The principle

> Preserve evidence. Remove invented rigor. State the strongest claim the evidence
> supports.

The skill does not ban technical terms or uncertainty. A supplied confidence
interval stays. A mathematically defined SVM margin stays. An interval fabricated
from a mean, or a "static probe" with no procedure or result, does not.

Every model-added analytical or formatting element is tested for:

1. provenance;
2. necessity;
3. interpretability;
4. decision value.

## Example

AI-defensive version:

> While these findings are promising, they should be interpreted with caution, and
> we cannot claim that the method consistently improves performance.

Evidence supplied: accuracy increases from 72.1% to 75.4% on Dataset A.

Clean version:

> The method improves accuracy from 72.1% to 75.4% on Dataset A.

The dataset name provides the exact boundary. The generic caution adds no useful
information.

## What the skill handles

- abstracts, introductions, results, discussions, and conclusions;
- captions and tables;
- AI-generated or AI-polished academic prose;
- overly cautious claims and unsolicited reviewer voice;
- unsupported statistical and methodological additions;
- em dashes, italics, bold text, and other synthetic formatting habits;
- abstract or difficult sentences that can be made concrete.

It has three modes:

- **Draft:** write from supplied facts without inventing analytical machinery;
- **Clean:** return a usable revision while preserving evidence and author voice;
- **Audit:** identify consequential artifacts and propose minimal repairs.

The Skill adapts those modes to the academic context: abstract and introduction,
methods, results, tables and captions, discussion and conclusion, or rebuttal and
review response.

## Severity model

Problems are ordered by consequence:

- **P0, evidence integrity:** changed or invented numbers, uncertainty, citations,
  equations, metrics, probes, experiments, conditions, or claim scope;
- **P1, analytical defensiveness:** reflexive caveats, unsupported interpretations,
  claim paralysis, vague abstraction, and reviewer voice;
- **P2, presentation residue:** gratuitous em dashes, italics, bold text,
  parentheticals, and table decoration.

P0 always outranks style. The Skill never makes a sentence cleaner by making its
evidence less accurate.

## Academic rewrite checker

The Skill includes an optional, zero-dependency Python checker for revisions where
both the original and edited files are available:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_academic_rewrite.py \
  before.md after.md
```

It checks deterministic invariants that a language model should not decide by
feel:

- numeric evidence;
- LaTeX citation and reference commands;
- bracketed numeric citations;
- math spans, URLs, fenced code, and Markdown heading levels;
- analytical constructs introduced only in the rewrite;
- new reviewer-voice caveats.

The checker does not classify text as human or AI. It protects academic evidence.
Use `--json` for machine-readable output. Use `--allow-new-analysis` or
`--allow-structure-change` only when the requested revision intentionally permits
those changes. When the author explicitly identifies a number as a fabricated or
unsourced draft artifact, pass `--allow-drop-number VALUE` once for each permitted
deletion. All other numeric drift remains a P0 error.

## Use it as a Skill

Copy the Skill directory into your agent's Skill directory. For Codex:

```bash
cp -r skills/anti-ai-defensive-writing ~/.codex/skills/
```

Then ask:

```text
Use $anti-ai-defensive-writing to clean this abstract without adding statistics or
weakening supported claims.
```

For other AI tools, copy [`prompts/quick-prompt.txt`](prompts/quick-prompt.txt) into
the beginning of a conversation.

## Repository structure

```text
anti-ai-defensive-writing/
├── .github/
│   ├── ISSUE_TEMPLATE/false-positive.yml
│   └── workflows/test.yml
├── skills/anti-ai-defensive-writing/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/check_academic_rewrite.py
├── prompts/quick-prompt.txt
├── evals/cases.md
├── tests/
├── scripts/check_policy_sync.py
├── CONTRIBUTING.md
└── LICENSE
```

## Boundaries

This skill does not perform statistical analysis, replace peer review, or justify
claims unsupported by evidence. It preserves legitimate uncertainty, technical
terms, and venue requirements. It removes model-added noise and unsupported rigor.

## Contributing

Contributions are welcome. The most useful changes begin with a realistic failure
case and an observable expected behavior. See [CONTRIBUTING.md](CONTRIBUTING.md).

Run the deterministic checks with:

```bash
python -m unittest discover -s tests -v
python scripts/check_policy_sync.py
```

## Acknowledgements

This project benefits from ideas explored across the open-source writing-tool
community, including the emphasis on preservation checks and false-positive
reporting in [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing).
The policy, academic context model, examples, evaluation cases, and checker in this
repository were designed and implemented independently for evidence-sensitive
academic revision.

## License

MIT
