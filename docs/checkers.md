# Checker reference

The repository includes three zero-dependency, read-only Python checkers. They do
not classify prose as human or AI. They protect evidence, manuscript structure,
bibliography metadata, and release-package surfaces that should not be decided by
style alone.

Commands below assume a cloned repository. For installed script locations, see
[Installation and updates](installation.md).

## Compare an academic rewrite

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_academic_rewrite.py \
  before.md after.md
```

The rewrite checker compares the original and edited files for:

- numeric evidence drift;
- changed LaTeX citations and references;
- changed bracketed numeric citations, math spans, URLs, or fenced code;
- changed Markdown heading levels;
- analytical constructs introduced only in the rewrite;
- new reviewer-voice caveats;
- newly introduced high-confidence cadence fillers, reported as review hints rather
  than automatic deletions.

The checker does not flag every parenthesis, comma, em dash, or isolated transition
word. It recognizes only a small set of high-confidence multiword patterns newly
added by the rewrite. The Skill then applies semantic deletion and truth-condition
tests to distinguish empty rhythm from a necessary scientific qualifier.

It preserves a user-supplied number even when the prose around it looks synthetic.
Only allow deletion when the author has explicitly identified that value as a
fabricated or source-free draft artifact.

| Option | Meaning |
| --- | --- |
| `--allow-new-analysis` | Permit analytical terms explicitly requested by the user |
| `--allow-structure-change` | Permit Markdown heading-level changes |
| `--allow-drop-number VALUE` | Permit one explicitly quarantined source number to be removed; repeat as needed |
| `--strict` | Treat warnings as failures |
| `--json` | Return machine-readable output |
| `--help`, `-h` | Print command help |

## Audit a LaTeX manuscript

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_manuscript_integrity.py \
  main.tex
```

The manuscript checker follows static `\input` and `\include` commands and
discovers `\bibliography` and `\addbibresource` files. It checks:

- unresolved or duplicate labels and citation keys;
- uncited figures and tables;
- first-citation order, missing labels or captions, and hard-coded display numbers;
- duplicate and unused BibTeX records;
- common required BibTeX fields and malformed DOI or URL values;
- acronyms used before definition, repeatedly undefined, or inconsistently cased.

Treat findings as source-located leads. Macro-generated references, custom
environments, venue conventions, and semantic terminology differences still need
contextual review.

| Option | Meaning |
| --- | --- |
| `--bib FILE` | Supply a BibTeX file that cannot be discovered; repeat as needed |
| `--known-acronym TERM` | Allow an explicit field-standard or venue-exempt acronym; repeat as needed |
| `--no-unused-bib` | Suppress unused-entry reports for a shared bibliography |
| `--verify-online` | Verify cited BibTeX metadata through Crossref with a DBLP fallback |
| `--verify-all-bib` | Verify every BibTeX entry instead of cited entries only |
| `--online-provider auto|crossref|dblp` | Select the metadata provider |
| `--mailto EMAIL` | Supply the optional Crossref polite-pool contact address |
| `--online-timeout SECONDS` | Set each provider-request timeout; default `10` |
| `--online-workers N` | Set concurrent lookups, capped at `8`; default `3` |
| `--strict` | Treat P1 and P2 findings as failures |
| `--json` | Return machine-readable output |
| `--help`, `-h` | Print command help |

### Online bibliography verification

Add one flag to combine local and online checks:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_manuscript_integrity.py \
  main.tex --verify-online
```

Online mode uses the documented
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
first and the
[DBLP publication search API](https://dblp.org/faq/How%2Bto%2Buse%2Bthe%2Bdblp%2Bsearch%2BAPI.html)
as a computer-science fallback. No API key or extra Python package is required.

Only cited records are queried by default. The checker sends a DOI, or the title,
first author, and year needed for matching. It does not upload manuscript prose or
modify `.bib` files.

Results use these states:

| State | Meaning |
| --- | --- |
| `verified` | Compared metadata agrees |
| `likely_match` | The record matches, but a field is incomplete or a venue alias needs review |
| `ambiguous` | More than one plausible record remains |
| `not_found` | Automatic verification found no exact match; this is not proof of fabrication |
| `conflicting_metadata` | Important supplied and source fields disagree |
| `provider_error` | The provider request failed |
| `unverifiable` | The record lacks enough metadata for a reliable query |

Metadata existence does not prove that a source supports a manuscript claim.
Claim-support auditing is a separate request that requires inspection of the cited
source. [Citesurely](https://citesurely.com/) and
[CiteScanning](https://www.modelscope.cn/studios/aivolcano/CiteScanning/summary)
remain optional manual second opinions; the checker does not depend on their hosted
interfaces or undocumented endpoints.

## Audit a release package

Double-blind review example:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  submission/ --release review --anonymity double-blind \
  --identity-term "Author Name" \
  --identity-term "github.com/author-account"
```

Publication or camera-ready example:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  camera-ready/ --release publication
```

| Option | Meaning |
| --- | --- |
| `--release review|publication` | Select the required release profile |
| `--anonymity none|single-blind|double-blind` | Select the venue review model; required for review packages |
| `--identity-term TERM` | Add a known name, username, affiliation, domain, project, or path fragment; repeat as needed |
| `--strict` | Treat P1 and P2 findings as failures |
| `--json` | Return machine-readable output |
| `--help`, `-h` | Print command help |

The checker scans deterministic surfaces and returns visual or media artifacts as
`manual_checks`. It does not perform OCR, interpret venue rules, inspect every
archive or office-document field, or certify anonymity. See
[Review and publication release audits](release-audits.md) for the complete
workflow.

## Severity and exit status

| Severity | Meaning |
| --- | --- |
| P0 | Evidence or release integrity: invented or changed evidence, broken references, conflicting keys, or identity exposure that violates the supplied release policy |
| P1 | Analytical, structural, terminology, metadata, or policy-dependent ambiguity requiring review |
| P2 | Presentation or package residue that is useful to clean but does not by itself invalidate the evidence |

P0 findings return exit status `1`. With `--strict`, P1 and P2 findings also return
`1`. Configuration errors return `2`. A zero exit status means that the checker
found no blocking deterministic issue; it does not override outstanding manual or
visual checks.
