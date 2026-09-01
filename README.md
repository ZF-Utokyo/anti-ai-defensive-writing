# Anti AI-Defensive Writing Skill

**English** · [简体中文快速上手](README.zh-CN.md)

> Struggling with em dashes, invented confidence intervals, fake metrics, and
> endless “we do not claim” disclaimers in AI-assisted academic writing?

An English, zero-dependency AI skill for removing unrequested caveats, faux rigor,
opaque abstraction, and formatting residue from academic writing without weakening
claims that the evidence supports. It also provides opt-in manuscript-integrity
audits for LaTeX references, figures, tables, BibTeX, acronyms, and terminology;
release-package audits for review anonymity and camera-ready identity; and an
evidence-grounded workflow for rebuttals and reviewer responses.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Test](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/actions/workflows/test.yml/badge.svg)](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/actions/workflows/test.yml)

## Quick start

Install the Skill for Codex:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex
```

Then paste a passage, attach a manuscript, or point Codex to a workspace file and
ask in natural language:

```text
Use $anti-ai-defensive-writing to clean this results section. Preserve every
number, citation, equation, and supported claim. Do not add analyses, metrics,
experiments, or reviewer-style caveats.
```

For a read-only LaTeX audit with online bibliography verification:

```text
Use $anti-ai-defensive-writing in Integrity mode. Audit main.tex, including
figures, tables, references, BibTeX, acronyms, and terminology. Run the bundled
checker with online reference verification. Do not modify my files.
```

For a reviewer response that does not invent promises:

```text
Use $anti-ai-defensive-writing to draft a rebuttal from the supplied review and
manuscript. Answer each concern with existing evidence and an exact location.
Do not promise new work unless I have approved it.
```

For a double-blind review package, including appendices and screenshots:

```text
Use $anti-ai-defensive-writing in Integrity mode to audit the exact upload package.
This is a double-blind review submission. Apply the supplied venue policy, run the
release checker, and visually inspect every PDF page, figure, and screenshot. Do
not modify my files or claim anonymity for anything you could not inspect.
```

Most users can stop here. Codex selects and runs the bundled checker when the task
needs deterministic validation.

## Skill and checkers

The Skill has two task paths:

| Path | Purpose |
| --- | --- |
| Paper | Draft, clean, or check manuscript prose, evidence, structure, and bibliography |
| Rebuttal | Map reviewer comments to existing evidence, exact locations, and authorized actions |

The Paper path has two release profiles:

| Release profile | Includes | Identity rule |
| --- | --- | --- |
| Review package | Submission, revision, and resubmission | Use the venue's explicit `none`, `single-blind`, or `double-blind` model |
| Publication package | Accepted and camera-ready material | Restore verified author-facing information and remove review-only placeholders |

The word "submission" never implies anonymity by itself. Rebuttal stays separate
because its primary artifact is a response to reviewer comments.

The repository also includes three deterministic safety nets for the Paper path:

| Component | Use it for | How to invoke it |
| --- | --- | --- |
| Skill | Drafting, cleaning, auditing, and evidence-aware judgment | Ask the agent using `$anti-ai-defensive-writing` |
| Rewrite checker | Comparing an original passage with an AI-edited version | Run `check_academic_rewrite.py before after` |
| Manuscript checker | Auditing a complete LaTeX project and its bibliography | Run `check_manuscript_integrity.py main.tex` |
| Release checker | Scanning the exact upload bundle for identity and packaging surfaces | Run `check_release_package.py PACKAGE --release ...` |

The checker scripts do not decide whether prose is human or AI. They protect
deterministic evidence, manuscript structure, and release-package surfaces, while
the Skill handles semantic questions such as whether a caveat is necessary or two
technical terms are truly equivalent.

The `npx` command installs the Skill; it does not expose a `check` subcommand.
An agent can run the bundled scripts for you. The shell commands below assume a
cloned repository. After a personal Codex installation, the scripts are under:

```text
~/.codex/skills/anti-ai-defensive-writing/scripts/
```

Claude uses `~/.claude/skills/anti-ai-defensive-writing/scripts/`, and a project
installation uses `./skills/anti-ai-defensive-writing/scripts/`.

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
- abstract or difficult sentences that can be made concrete;
- rebuttals, responses to meta-reviews, and revision letters;
- double-blind review bundles and camera-ready de-anonymization;
- optional figure/table, cross-reference, BibTeX, acronym, and terminology audits.

It has four modes:

- **Draft:** write from supplied facts without inventing analytical machinery;
- **Clean:** return a usable revision while preserving evidence and author voice;
- **Audit:** identify consequential artifacts and propose minimal repairs;
- **Integrity:** audit manuscript structure, metadata, and release packaging without
  silently editing it.

The Skill adapts those modes to the academic context: abstract and introduction,
methods, results, tables and captions, discussion and conclusion, or rebuttal and
review response.

For complete manuscripts, it builds an internal evidence ledger before editing:
claims map to supplied results, tables, citations, equations, methods, scope, and
material uncertainty. It then removes cross-section caveat duplication by meaning,
not by phrase count. The ledger is not a style score and is not returned unless the
user requests it.

## Severity model

Problems are ordered by consequence:

- **P0, evidence or release integrity:** changed or invented numbers, uncertainty,
  citations, equations, metrics, probes, experiments, conditions, claim scope,
  unresolved references, conflicting keys, or identity exposure that violates the
  supplied release policy;
- **P1, analytical defensiveness:** reflexive caveats, unsupported interpretations,
  claim paralysis, vague abstraction, reviewer voice, and structural or terminology
  ambiguities, plus policy-dependent identity surfaces that need verification;
- **P2, presentation residue:** gratuitous em dashes, italics, bold text,
  parentheticals, table decoration, package residue, and other nonblocking cleanup.

P0 always outranks style. The Skill never makes a sentence cleaner by making its
evidence less accurate.

## Checkers

### Compare an academic rewrite

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

### Audit a LaTeX manuscript

The optional integrity workflow keeps structural checks separate from prose
cleanup. For a LaTeX project, run:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_manuscript_integrity.py \
  main.tex
```

The zero-dependency checker follows static `\input` and `\include` commands and
discovers `\bibliography` and `\addbibresource` files. It reports:

- unresolved or duplicate labels and citation keys;
- figures and tables that are uncited, out of first-citation order, missing labels
  or captions, or referenced with hard-coded numbers;
- duplicate and unused BibTeX records, common missing fields, and malformed DOI or
  URL values;
- acronyms used before definition, repeated without a definition, or used with
  inconsistent casing.

Use `--bib FILE` when a bibliography cannot be discovered, `--no-unused-bib` for a
shared library, `--known-acronym TERM` for an explicit field or venue exemption,
`--json` for structured output, and `--strict` to fail on warnings. The default
command is offline and read-only.

For one-command local and online verification, add one flag:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_manuscript_integrity.py \
  main.tex --verify-online
```

This queries the
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
first and falls back to the
[DBLP publication search API](https://dblp.org/faq/How%2Bto%2Buse%2Bthe%2Bdblp%2Bsearch%2BAPI.html)
when Crossref does not return an exact normalized-title match. No API key or extra
Python package is required.
Only BibTeX entries cited by the manuscript are queried by default; use
`--verify-all-bib` to check the whole bibliography. `--online-provider` can pin a
provider, `--mailto` supplies the optional Crossref contact address, and
`--online-timeout` and `--online-workers` control requests.

Semantic terminology consistency remains an agent task: the Skill builds an
internal ledger of canonical terms, first definitions, abbreviations, variants,
and intentional distinctions across the abstract, body, captions, tables, and
supplement.

`--verify-online` sends only the title, first author, year, and DOI needed for a
lookup. It does not upload the manuscript and never changes the paper or `.bib`
file. Results are reported as `verified`, `likely_match`, `ambiguous`,
`not_found`, `conflicting_metadata`, `provider_error`, or `unverifiable`, with
field differences and source links where available. A missing result is not proof
of a fabricated reference, and metadata existence is not proof that a source
supports a claim.

[Citesurely](https://citesurely.com/) and
[CiteScanning](https://www.modelscope.cn/studios/aivolcano/CiteScanning/summary)
remain optional manual second opinions; the one-command path does not depend on
their hosted interfaces or undocumented endpoints. Claim-support auditing is a
separate, explicit request. An excerpt without its Results section is not evidence
that the full manuscript lacks support.

### Audit a review or publication package

Run the release checker on the exact directory or file that will be uploaded. A
double-blind review example is:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  submission/ --release review --anonymity double-blind \
  --identity-term "Author Name" \
  --identity-term "github.com/author-account"
```

For non-anonymous or single-blind review, use `--anonymity none` or
`--anonymity single-blind`. For camera-ready material, run:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  camera-ready/ --release publication
```

The zero-dependency, read-only checker scans package paths, readable source files,
common LaTeX identity fields, emails, ORCID identifiers, local home paths,
repository URLs, accessible PDF author metadata, review placeholders, archives,
and packaging residue. Repeated `--identity-term` flags add known names, usernames,
affiliations, domains, project names, or path fragments. Use specific terms; a
surname alone can collide with a legitimate bibliography entry.

Visual artifacts are returned separately as manual checks. The Skill should render
every submitted PDF page and inspect appendices, figures, screenshots, slides, and
videos for names, avatars, account menus, browser tabs, terminal paths, comments,
watermarks, and participant or annotator identity. The script does not perform OCR
or interpret venue rules, inspect office-document internals, or reliably read
compressed metadata. A clean text scan never certifies anonymity. If the current
policy, an archive, metadata, linked resource, or visual artifact cannot be checked,
the result remains `unresolved`.

### Understand checker results

P0, P1, and P2 follow the [severity model](#severity-model) above. By default, a
checker exits with status 1 for a P0 failure; `--strict` also fails on P1 and P2
findings. Configuration errors return status 2.

Online bibliography results use these states:

- `verified`: the compared fields agree;
- `likely_match`: the record matches, with incomplete fields or a possible venue
  alias to review;
- `ambiguous` or `not_found`: automatic verification is inconclusive, not proof of
  fabrication;
- `conflicting_metadata`: important supplied and source fields disagree;
- `provider_error` or `unverifiable`: the provider failed or the record lacks
  enough query metadata.

Release-checker output separates deterministic `findings` from `manual_checks`.
For review packages, `--anonymity` is required so the checker never silently assumes
that a submission is double-blind.

## Installation options

Inspect the resolved target without writing files:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex --dry-run
```

Supported destinations are `codex`, `claude`, and `project`. Use `--dir PATH` to
select another parent directory. Existing installations are refused by default;
`--force` moves the old installation to a timestamped backup before replacing it.

Install for Claude or the current project:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent claude
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent project
```

Manual installation also remains available. Copy the Skill directory into the
agent's Skill directory. For Codex:

```bash
cp -r skills/anti-ai-defensive-writing ~/.codex/skills/
```

## Ready-to-use prompts

- [Clean a passage](prompts/quick-prompt.txt)
- [Audit without a full rewrite](prompts/audit-prompt.txt)
- [Clean a complete manuscript](prompts/full-manuscript-prompt.txt)
- [Audit manuscript integrity](prompts/integrity-prompt.txt)
- [Draft or clean a rebuttal](prompts/rebuttal-prompt.txt)
- [Audit a review or publication package](prompts/release-audit-prompt.txt)

These are task entry points, not separate policy implementations. The repository
checks that they retain the same evidence-integrity rules as the Skill.

## Boundaries

This skill does not perform statistical analysis, replace peer review, or justify
claims unsupported by evidence. It preserves legitimate uncertainty, technical
terms, and venue requirements. It does not upload private bibliographies, silently
renumber displays, replace records, or declare citations hallucinated from a failed
metadata search. It removes model-added noise and unsupported rigor.
It also does not certify anonymity from text alone or reveal participant and
annotator identity merely because the authors are de-anonymized for publication.

## Contributing

Contributions are welcome. The most useful changes begin with a realistic failure
case and an observable expected behavior. See [CONTRIBUTING.md](CONTRIBUTING.md).

Run the deterministic checks with:

```bash
node --test tests/test_installer.mjs
python3 -m unittest discover -s tests -v
python3 scripts/check_policy_sync.py
npm pack --dry-run
```

## License

MIT
