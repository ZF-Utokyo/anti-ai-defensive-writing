# Manuscript integrity audit

Use this optional workflow when the user asks for submission checks, figure or
table references, citation order, BibTeX validation, acronym definitions, or
terminology consistency. Do not run it automatically for an ordinary prose
cleanup.

## Contents

- Separate deterministic and semantic checks
- Check figures and tables
- Check citations and BibTeX
- Check terminology
- Return actionable findings

## Separate deterministic and semantic checks

Run deterministic checks on LaTeX and BibTeX files when they are available:

    python3 scripts/check_manuscript_integrity.py main.tex

For one-command local and online metadata verification, after the user authorizes
network access:

    python3 scripts/check_manuscript_integrity.py main.tex --verify-online

The checker follows static \input and \include commands and discovers
\bibliography and \addbibresource files. Use --bib FILE for a bibliography that
cannot be discovered. Use --json for structured output, --strict to fail on P1 and
P2 findings, --no-unused-bib for a shared library, and --known-acronym TERM only
for an explicit field or venue exemption. Online mode verifies cited entries by
default. Use --verify-all-bib for the full library, --online-provider to pin
Crossref or DBLP, --mailto for the optional Crossref contact address, and
--online-timeout or --online-workers to tune requests.

Treat script findings as leads with source locations. Inspect macro-generated
references, custom environments, and venue conventions manually. Do not rewrite
labels, keys, numbering, or bibliography records without the user's authorization.

## Check figures and tables

Build a display ledger with the display label, caption, source location, first
in-text citation, and referenced panels.

- Confirm that every figure and table has a stable label and a useful caption.
- Confirm that every display is cited in the manuscript and every citation resolves.
- Compare figure and table numbering separately with their first-citation order.
- Check panel references, supplementary prefixes, and ranges such as
  Figures 2--4 in context.
- Prefer \ref, \autoref, or the project's established command over hard-coded
  display numbers.
- Compare the prose, caption, axes, headers, units, sample sizes, and displayed
  values when the source artifacts are available.

Judge order by the first meaningful in-text citation, not by rendered page position.
LaTeX floats can move. Respect a venue rule that intentionally uses a different
order or permits a display before its first mention.

## Check citations and BibTeX

First verify local consistency:

- resolve every citation key against the discovered bibliography;
- detect duplicate keys and likely duplicate records;
- report unused entries unless the bibliography is intentionally shared;
- check common required fields, DOI shape, and HTTP(S) URLs;
- preserve BibTeX braces that protect capitalization in names and technical terms.

Then verify metadata externally only when the user requests it and network access
is available. The bundled one-command route uses the documented
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
first and the
[DBLP publication search API](https://dblp.org/faq/How%2Bto%2Buse%2Bthe%2Bdblp%2Bsearch%2BAPI.html)
as a fallback.

- Prefer an exact DOI lookup. Without a DOI, require an exact normalized-title
  match before comparing authors, year, venue, and DOI.
- Use Crossref for broad scholarly metadata and DBLP as a computer-science
  fallback. Do not treat either source as complete.
- Use [Citesurely](https://citesurely.com/) as an optional manual comparison of
  title, author, year, and venue. Do not assume a private or stable API.
- Use [CiteScanning](https://www.modelscope.cn/studios/aivolcano/CiteScanning/summary)
  as an optional manual or self-hosted multi-source check. Do not copy its code or
  make its hosted interface a required dependency.

Online mode sends the DOI, or a query composed from the title, first author, and
year. It never uploads manuscript prose. Do not send these fields without the
user's authorization, scrape a service, bypass limits, or depend on an
undocumented endpoint.

Record each external result as verified, likely_match, ambiguous, not_found,
conflicting_metadata, provider_error, or unverifiable. A missing result is not proof
that a reference is fabricated. Never replace a BibTeX record automatically; show
the compared fields and authoritative link for author confirmation.

Bibliographic existence and citation support are different questions. Metadata can
confirm that a work exists. It cannot establish that the work supports a sentence.
Do not start a claim-support audit unless the user requests one. Do not infer that
a manuscript claim lacks evidence merely because the supplied material is an
excerpt or omits its Results section. For a requested claim-support audit, inspect
the cited source and record the exact passage, figure, table, or theorem that bears
on the claim. Mark inaccessible evidence as unverified rather than guessing.

## Check terminology

Build a terminology ledger internally:

- **Canonical term:** the exact form to use.
- **Definition anchor:** the first meaningful definition.
- **Abbreviation:** the approved short form, if any.
- **Variants:** alternative casing, hyphenation, spelling, or near-synonyms found.
- **Scope note:** any intentional distinction between related terms.

Define a nonstandard term or acronym at first meaningful use, then use the
canonical form consistently. Audit the title, abstract, main text, captions,
tables, appendices, and supplementary material. Treat the abstract as an
independent reading unit when the venue expects abbreviations to be expanded there.

Do not merge terms merely because they look similar. Preserve distinctions between
a task and dataset, a model family and implementation, a metric and proxy, or a
general method and one configuration. Do not vary technical terms only to avoid
repetition.

## Return actionable findings

Report source location, observed evidence, consequence, and smallest repair.
Separate P0 broken or conflicting references, P1 structural or terminology
ambiguities, and P2 cleanup findings. Do not assign an integrity score, predict a
reviewer reaction, or claim that an external service has proved a citation valid.
Stay within the requested audit surfaces and do not turn missing context into
unsolicited peer review.
