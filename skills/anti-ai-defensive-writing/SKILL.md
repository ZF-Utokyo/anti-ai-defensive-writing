---
name: anti-ai-defensive-writing
description: >
  Draft or revise academic writing without unrequested AI defensiveness: reflexive
  caveats, unsupported statistical machinery, invented metrics or probes,
  gratuitous em dashes or italics, opaque abstraction, and claims weakened below
  what the evidence supports. Use for cleaning AI-generated abstracts, papers,
  methods, results, captions, tables, conclusions, and rebuttals while preserving
  facts and legitimate uncertainty. Do not use this skill to conduct statistical
  analysis or peer review itself.
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

Infer the mode from the request. Ask only when different modes would produce
materially different deliverables.

Match the passage to its academic context before revising. Read only the relevant
section of [context-profiles.md](references/context-profiles.md) for abstracts and
introductions, methods, results, tables and captions, discussions and conclusions,
or rebuttals and review responses.

When the supplied material spans multiple manuscript sections, also read
[whole-manuscript-workflow.md](references/whole-manuscript-workflow.md). Build its
claim-to-evidence ledger internally, reconcile repeated caveats by meaning, and run
the final integrity pass across section boundaries.

## Apply the four tests

For each qualifier, statistic, metric, probe, formatting choice, or methodological
claim, ask:

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

- **P0, evidence integrity:** changed or invented numbers, uncertainty, citations,
  equations, metrics, probes, experiments, conditions, or claim scope. Never trade
  evidence integrity for cleaner style.
- **P1, analytical defensiveness:** reflexive caveats, unsupported interpretations,
  claim paralysis, vague abstraction, reviewer voice, or unnecessary analytical
  commitments.
- **P2, presentation residue:** gratuitous em dashes, italics, bold text,
  parentheticals, table decoration, or other formatting that adds no meaning.

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
- Preserve the author's level of formality and terminology. Remove AI residue
  without flattening a distinctive voice.

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
4. no new reviewer-voice caveat or formatting artifact was introduced.

For file-based rewrites or passages with quantitative evidence, run the bundled
checker when both versions are available:

```bash
python3 scripts/check_academic_rewrite.py before.md after.md
```

Treat P0 errors as blocking. Inspect P1 warnings in context. Use
`--allow-new-analysis` or `--allow-structure-change` only when the user's request
explicitly authorizes that change. Use `--allow-drop-number VALUE` only for a value
the user has explicitly quarantined as an unsupported draft artifact.

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

## Final check

- No facts or supplied uncertainty were lost.
- No statistic, metric, analysis, citation, or experiment was invented.
- The claim is neither broader nor weaker than the evidence supports.
- Technical terms are defined and relevant.
- Formatting helps interpretation rather than simulating sophistication.
- The result reads like an author communicating evidence, not an AI anticipating
  every possible reviewer objection.
