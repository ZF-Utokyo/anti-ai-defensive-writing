# Whole-manuscript workflow

Use this workflow only when the supplied material spans multiple paper sections.
Keep the evidence ledger internal unless the user asks to see it. Do not turn it
into a score or a large style report.

## Build an evidence ledger

Create a compact record for each consequential claim:

- **Claim anchor:** the section and sentence that states the claim.
- **Evidence anchor:** the supplied result, table, citation, equation, or method
  definition that supports it.
- **Allowed scope:** the dataset, population, comparison, condition, or theorem
  boundary the evidence covers.
- **Uncertainty:** supplied intervals, variation, sample size, assumptions, or
  limitations that materially change interpretation.
- **Caveat home:** the one or two locations where a material limitation helps the
  reader, rather than every location where the claim appears.
- **Quarantined artifact:** any quantity, metric, analysis, or interpretation the
  user identifies as model-added or unverified.

If a claim has no evidence anchor, do not manufacture one. Remove the unsupported
interpretation in Clean mode or report the missing link in Audit mode.

## Audit in evidence order

1. Read Methods, Results, tables, and captions to establish what was actually done
   and observed.
2. Map the Abstract, contribution statements, Discussion, and Conclusion to those
   evidence anchors.
3. Check Limitations for conditions that genuinely change interpretation.
4. Treat rebuttal text as a separate response context; do not let promises or
   reviewer language leak into the manuscript.

This order establishes evidence before editing high-visibility claims. It is not a
required output order.

## Detect semantic repetition

Represent each caveat by its meaning: affected claim, limiting condition, and
interpretive consequence. Two differently worded sentences are duplicates when
those three elements are the same and the later sentence adds no new decision
value.

- Keep a short scope boundary in the Abstract when readers would otherwise
  misunderstand the headline result.
- Keep the full material limitation near the relevant interpretation or in the
  Limitations section.
- Remove repeated denials, speculative failure catalogs, and section-ending
  disclaimers that add no new condition.
- Do not delete a repeated caveat merely to reach one occurrence. Preserve it where
  each occurrence serves a distinct reader need or venue requirement.

Do not count phrases as a substitute for this semantic check.

## Revise locally, then reconcile globally

Edit the smallest useful span in each section. After local edits:

1. confirm that every surviving claim maps to the same evidence and scope;
2. confirm that numbers, citations, equations, uncertainty, and experimental
   conditions remain unchanged;
3. confirm that quarantined artifacts are removed only with explicit authorization;
4. confirm that deleting a duplicate did not remove the only statement of a
   material limitation;
5. run the bundled checker on file-based before/after versions when available.

In Clean mode, return the revised manuscript or requested sections first. In Audit
mode, group consequential findings by P0, P1, and P2 and name the smallest repair.
Do not add a paper-level defensiveness score or predict reviewer reactions.
