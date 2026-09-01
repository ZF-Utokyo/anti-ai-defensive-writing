# Anti AI-Defensive Writing Skill

**English** · [简体中文快速上手](README.zh-CN.md)

> Struggling with em dashes, invented confidence intervals, fake metrics, and
> endless “we do not claim” disclaimers in AI-assisted academic writing?

Anti AI-Defensive Writing removes unsupported caveats, invented rigor, opaque
abstraction, and formatting residue while preserving the evidence and uncertainty
that the author actually supplied.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Test](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/actions/workflows/test.yml/badge.svg)](https://github.com/ZF-Utokyo/anti-ai-defensive-writing/actions/workflows/test.yml)

## Install

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex
```

Then paste text, attach a manuscript, or point Codex to workspace files. Most users
do not need to run the bundled checkers themselves.

## Three copy-and-paste entry points

### Clean academic writing

```text
Use $anti-ai-defensive-writing to clean this results section. Preserve every
number, citation, equation, and supported claim. Do not add analyses, metrics,
experiments, or reviewer-style caveats.
```

### Audit a review or camera-ready package

```text
Use $anti-ai-defensive-writing in Integrity mode to audit the exact upload package.
Apply the supplied venue policy, run the release checker, and visually inspect
every PDF page, figure, and screenshot. Do not modify my files or claim anonymity
for anything you could not inspect.
```

For review packages, state `none`, `single-blind`, or `double-blind`. The word
"submission" does not imply anonymity by itself.

### Draft a rebuttal

```text
Use $anti-ai-defensive-writing to draft a rebuttal from the supplied review and
manuscript. Answer each concern with existing evidence and an exact location. Do
not promise new work unless I have approved it.
```

## Two task paths

| Path | Purpose |
| --- | --- |
| **Paper** | Draft, clean, or audit manuscript prose, evidence, structure, bibliography, and release packages |
| **Rebuttal** | Map reviewer comments to existing evidence, exact locations, and authorized actions |

Paper work uses two release profiles:

| Release profile | Includes | Identity rule |
| --- | --- | --- |
| **Review package** | Submission, revision, and resubmission | Use the venue's explicit `none`, `single-blind`, or `double-blind` model |
| **Publication package** | Accepted and camera-ready material | Restore verified author-facing information and remove review-only placeholders |

Rebuttal remains separate because its primary artifact is a response to reviewer
comments, not the paper itself.

## Before and after

AI-defensive draft:

> While these findings are promising, they should be interpreted with caution, and
> we cannot claim that the method consistently improves performance.

Supplied evidence: accuracy increases from 72.1% to 75.4% on Dataset A.

Clean version:

> The method improves accuracy from 72.1% to 75.4% on Dataset A.

The dataset states the real boundary. The generic warning adds no evidence. The
core rule is simple:

> Preserve evidence. Remove invented rigor. State the strongest claim the evidence
> supports.

## Three deterministic checkers

| Checker | Protects | Direct command |
| --- | --- | --- |
| Rewrite checker | Numbers, citations, equations, URLs, structure, and newly invented analysis | `check_academic_rewrite.py before after` |
| Manuscript checker | LaTeX references, figure/table order, BibTeX, acronyms, and terminology leads | `check_manuscript_integrity.py main.tex`; add `--verify-online` for Crossref with a DBLP fallback |
| Release checker | Review anonymity, camera-ready identity, metadata, file paths, and upload-package residue | `check_release_package.py PACKAGE --release ...` |

The scripts are zero-dependency and read-only. They do not decide whether text is
human or AI. The Skill handles semantic judgment; the checkers protect deterministic
surfaces and report anything that still requires visual or policy review.

## Documentation

- [Installation, destinations, updates, and backups](docs/installation.md)
- [Checker commands, every option, severity, and result meanings](docs/checkers.md)
- [Review anonymity and camera-ready release audits](docs/release-audits.md)
- [Ready-to-use prompts](prompts/)
- [Skill policy and workflow](skills/anti-ai-defensive-writing/SKILL.md)
- [Evaluation cases](evals/cases.md)

## Contributing

Contributions are welcome, especially realistic false positives and failure cases
with observable expected behavior. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
