---
name: anti-ai-defensive-writing
description: >
  Draft or revise academic writing without unrequested AI defensiveness: reflexive
  caveats, unsupported statistical machinery, invented metrics or probes,
  rhetorical insertions that manufacture cadence, gratuitous em dashes or italics,
  opaque abstraction, and claims weakened below what the evidence supports. Use for
  cleaning AI-generated abstracts, papers, methods, results, captions, tables, and
  conclusions while preserving facts and legitimate uncertainty; for
  evidence-grounded rebuttals, reviewer responses, and revision letters; for
  review-package anonymity and camera-ready release audits; or for optional
  manuscript-integrity audits of LaTeX cross-references, figure and table order,
  BibTeX records, acronyms, and terminology. Do not use this skill to conduct
  statistical analysis or peer review itself.
---

# Anti AI-Defensive Writing Skill

Produce direct, evidence-aligned academic prose. Remove AI additions that create
analytical commitments, reviewer attack surfaces, or visual noise without helping
the reader understand the work.

## Non-negotiable boundaries

1. Preserve the user's factual content, numbers, citations, equations, scope
   conditions, and required venue conventions. Unsupported interpretations,
   evaluative labels, and disclaimers are not facts merely because they appear in
   the source draft.
2. Never invent data, confidence intervals, significance tests, effect sizes,
   margins, probes, metrics, experiments, citations, or methodological details.
3. State the strongest claim the supplied evidence supports. Do not strengthen it
   past the evidence or weaken it into reflexive uncertainty.
4. Treat user-supplied statistics as evidence unless the user explicitly identifies
   them as model-added, unverified, fabricated, or source-free. Remove such
   quarantined artifacts in Clean mode; retain and label them only when the user
   asks to audit or trace them. If the status of a quantity is unclear, flag it once
   or ask for its source instead of guessing.
5. Do not turn editing into unsolicited peer review. Raise a validity problem only
   when it materially changes the requested claim or output.

## Choose the operating mode

- **Draft:** Write from supplied facts without adding analytical machinery.
- **Clean (default for revision requests):** Return a usable revision, preserving
  the author's meaning and structure unless restructuring is requested.
- **Audit:** Identify defensive or synthetic AI artifacts and propose repairs
  without rewriting the full passage.
- **Integrity (opt-in):** Audit manuscript structure, bibliography metadata, and
  terminology without rewriting prose or silently changing records.

Infer the mode from the request. Ask only when different modes would produce
materially different deliverables.

Match the passage to its academic context before revising. Read only the relevant
section of [context-profiles.md](references/context-profiles.md) for abstracts and
introductions, methods, results, tables and captions, discussions and conclusions,
or other manuscript prose.

When the user asks for a rebuttal, author response, response to a meta-review, or
revision letter, read
[rebuttal-workflow.md](references/rebuttal-workflow.md). Keep the paper and the
review response as separate evidence surfaces. Build the comment-to-evidence ledger
internally, ground each response in an exact location, and do not promise
unapproved work.

When the supplied material spans multiple manuscript sections, also read
[whole-manuscript-workflow.md](references/whole-manuscript-workflow.md). Build its
claim-to-evidence ledger internally, reconcile repeated caveats by meaning, and run
the final integrity pass across section boundaries.

When the user explicitly asks about figure or table citations, reference order,
LaTeX labels, BibTeX validity, citation existence, acronym definitions, or
terminology consistency, read
[manuscript-integrity.md](references/manuscript-integrity.md). Keep that optional
audit separate from ordinary prose cleanup. Run deterministic local checks before
semantic or external checks, and never treat a metadata search result as proof
that a cited work supports a claim.

When the user asks whether a submission, revision, resubmission, camera-ready paper,
or supplementary bundle is ready to upload, or asks for an anonymity or identity
audit, read [release-package.md](references/release-package.md). Keep this inside
the Paper path. Select either a review package with the venue's explicit `none`,
`single-blind`, or `double-blind` anonymity model, or a publication package. Audit
the exact upload bundle, including metadata and visual artifacts; never infer that
all submissions are anonymous or claim that a text scan proves anonymity.

## Apply the four tests

For each qualifier, rhetorical insertion, statistic, metric, probe, formatting
choice, or methodological claim, ask:

1. **Provenance:** Is it supplied by the user or a cited source?
2. **Necessity:** Is it required by the task, analysis, or venue?
3. **Interpretability:** Is it defined well enough for the reader to understand?
4. **Decision value:** Does it change the interpretation of the evidence?

Keep source-backed evidence. Keep required elements. Clarify elements that are
necessary but undefined. Remove model-added elements that have no defensible
source, requirement, or interpretive value. Present genuinely useful new analysis
only as an explicit proposal, never as completed work.

## Triage by consequence

Assign the highest applicable severity and resolve higher-severity problems first:

- **P0, evidence or release integrity:** changed or invented numbers, uncertainty,
  citations, equations, metrics, probes, experiments, conditions, or claim scope;
  unresolved references or conflicting keys; or identity exposure that violates the
  supplied release policy. Never trade evidence or release integrity for cleaner
  style.
- **P1, analytical defensiveness:** reflexive caveats, unsupported interpretations,
  claim paralysis, vague abstraction, reviewer voice, unnecessary analytical
  commitments, rhetorical insertions that add unsupported evaluation, structural
  and terminology ambiguities, or policy-dependent identity surfaces that need
  verification.
- **P2, presentation residue:** gratuitous em dashes, italics, bold text,
  cadence-only parentheticals, table decoration, unused records, package residue,
  or other nonblocking cleanup.

In Audit mode, report this severity with each consequential finding. Do not label a
defined technical term or explicit style choice as a problem merely because it
resembles an AI habit.

## Clean the prose

- Replace caveat stacks with one exact scope statement where scope matters.
- Remove reviewer-voice filler such as "while promising," "should be interpreted
  with caution," and "we cannot claim" when it adds no specific information.
- Prefer concrete subjects, actions, measurements, and outcomes over abstract noun
  chains such as "a multidimensional lens for interrogating latent dynamics."
- Remove unsupported evaluative labels such as "simple," "robust," "comprehensive,"
  and "novel" when the supplied material does not define or demonstrate them.
- Use technical terms only when they are defined and necessary. Words such as
  "margin," "probe," and "robustness" are not banned; unsupported uses are.
- Do not add em dashes. Replace gratuitous em dashes in editable prose with a
  period, comma, colon, or parentheses. Preserve them when the user explicitly
  requests that style or when quoted text must remain exact.
- Use italics and bold only when they carry a required semantic or style function.
  Do not use typography to manufacture emphasis or novelty.
- Remove rhetorical insertions that manufacture cadence, importance, or surprise
  without adding evidence, scope, definition, attribution, or meaning. Preserve a
  scientific qualifier when deleting it would change when the claim is true.
- Preserve the author's level of formality and terminology. Remove AI residue
  without flattening a distinctive voice.

For comma-bounded asides, parentheticals, sentence-interrupting transitions, or
evaluative em-dash insertions, read
[rhetorical-insertions.md](references/rhetorical-insertions.md). Apply its deletion
and truth-condition tests; do not ban punctuation or isolated words.

## Calibrate claims

- Turn vague hedging into an exact condition: name the evaluated dataset, setting,
  population, or comparison when that boundary is supplied.
- Make descriptive results declarative. An observed improvement can be stated as
  an improvement in the evaluated setting without "may suggest."
- Do not convert association into causation or evaluated performance into universal
  generalization.
- When a concept appears only in an unsupported interpretation or its defensive
  denial, omit that concept entirely and report the supported result. Do not replace
  it with "we cannot claim X" or "this does not establish X." Mention it only when
  the user asks whether that claim is supportable or when omitting it would
  materially mislead the reader.
- When evidence limits a claim, narrow the claim once and state the result directly.
  Do not append a paragraph of speculative failure modes.

For results, uncertainty, metrics, statistical tests, or experimental claims, read
[evidence-and-statistics.md](references/evidence-and-statistics.md).

For tables, captions, emphasis, or document-level formatting, read
[tables-and-formatting.md](references/tables-and-formatting.md).

When a pattern remains ambiguous or the user asks for an explanation, consult
[examples.md](references/examples.md).

## Run one integrity pass

After drafting or cleaning, compare the revision with the supplied source once.
Patch only the remaining problem; do not regenerate the passage stylistically.

Check that:

1. every number, citation, equation, unit, uncertainty statement, and scope
   condition still maps to its source;
2. no statistic, metric, probe, experiment, causal mechanism, or reference appeared
   without support;
3. the claim remains the strongest one the evidence supports;
4. no new reviewer-voice caveat, cadence-only insertion, or formatting artifact was
   introduced.

For file-based rewrites or passages with quantitative evidence, run the bundled
checker when both versions are available:

```bash
python3 scripts/check_academic_rewrite.py before.md after.md
```

Treat P0 errors as blocking. Inspect P1 warnings in context. Use
`--allow-new-analysis` or `--allow-structure-change` only when the user's request
explicitly authorizes that change. Use `--allow-drop-number VALUE` only for a value
the user has explicitly quarantined as an unsupported draft artifact.

For a LaTeX manuscript-integrity request, run the second bundled checker:

    python3 scripts/check_manuscript_integrity.py main.tex

It follows static includes and checks local labels, references, display order,
BibTeX keys and common metadata, hard-coded display numbers, and acronym use. Treat
its findings as source-located leads, not automatic edits.

When the user authorizes online metadata verification, run the same check in one
step:

    python3 scripts/check_manuscript_integrity.py main.tex --verify-online

This checks cited BibTeX records through Crossref with a DBLP fallback, using exact
DOI or normalized-title matching before comparing fields. It sends bibliographic
query fields, not manuscript prose, and never edits `.bib` automatically. Use the
JSON option for structured output and consult the manuscript-integrity reference
for privacy boundaries, result meanings, and terminology decisions.

For a deterministic review-package scan, require the venue's anonymity model and
run:

    python3 scripts/check_release_package.py submission/ \
      --release review --anonymity double-blind \
      --identity-term "Author Name"

For a camera-ready or accepted package, run:

    python3 scripts/check_release_package.py camera-ready/ --release publication

Use the exact upload directory. Inspect every reported visual or media artifact
with available rendering tools. If an artifact, archive, metadata surface, linked
resource, or venue rule cannot be checked, report it as unresolved rather than
certifying the package.

## Output contract

For Draft or Clean mode:

1. Give the revised text or table first.
2. Add a short note only for a material ambiguity, unsupported element, or requested
   explanation.
3. Do not produce an unsolicited style lecture, reviewer report, or catalog of
   hypothetical limitations.

For Audit mode, report each consequential finding as: severity, artifact, why it is
a problem here, and the smallest useful repair. Do not flag a harmless pattern
merely because it resembles a common AI habit. Do not assign a paper-level
defensiveness score or predict reviewer reactions.

For Integrity mode, report severity, source location, observed evidence, and the
smallest repair. Do not rewrite, renumber, replace bibliography records, upload
private files, or query external services unless the user requests the relevant
action. Report a missing external result as unresolved evidence, not as a
hallucinated citation. Stay within the requested audit surfaces. Do not infer that
a claim lacks evidence merely because the user supplied an excerpt, and do not
start a claim-support audit unless requested. For release audits, state the selected
profile and policy, separate deterministic findings from visual or manual checks,
and conclude ready, not ready, or unresolved without overstating coverage.

## Final check

- No facts or supplied uncertainty were lost.
- No statistic, metric, analysis, citation, or experiment was invented.
- The claim is neither broader nor weaker than the evidence supports.
- Technical terms are defined and relevant.
- Cadence-only insertions are gone, while evidence-bearing qualifiers remain.
- Formatting helps interpretation rather than simulating sophistication.
- A requested release audit used the correct venue policy and exact upload bundle.
- The result reads like an author communicating evidence, not an AI anticipating
  every possible reviewer objection.
