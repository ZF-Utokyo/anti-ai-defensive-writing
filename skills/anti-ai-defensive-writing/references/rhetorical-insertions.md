# Rhetorical insertions

Treat sentence interruptions as a semantic decision, not a punctuation ban.
AI-generated prose often inserts an aside to manufacture importance, surprise, or
cadence even though the aside changes no fact. Parentheses, commas, and em dashes
can also carry necessary scientific information.

## Apply two tests

1. **Deletion test:** Remove the insertion and read the sentence again. If its
   factual content, scope, and logic are unchanged, the insertion is a candidate
   for deletion.
2. **Truth-condition test:** Ask whether the insertion supplies a condition,
   population, comparison, definition, attribution, citation, uncertainty measure,
   or other information that changes when the statement is true. If it does,
   preserve that information.

Then choose the smallest repair:

- Delete a cadence-only aside.
- Integrate useful information into the main clause, or split the sentence when the
  interruption obscures the logic.
- Preserve a necessary scientific qualifier, even when it is parenthetical.
- Replace unsupported evaluation with supplied evidence. Do not translate
  `surprisingly strong` into another adjective when a result can be stated.

## Review candidates in context

Common candidates include comma-bounded or em-dash phrases such as `perhaps more
importantly`, `perhaps more surprisingly`, `it is worth noting that`, `despite its
apparent simplicity`, and `while seemingly simple`. Sentence-medial adverbs such as
`importantly`, `notably`, and `crucially` also deserve review when they merely tell
the reader how to react.

These are review candidates, not banned phrases. For example, `in practice` can
mark a real distinction between a theoretical guarantee and an implementation;
`notably` can introduce a contrast established by the supplied evidence. Do not
delete either merely because it resembles an AI habit.

## Examples

Cadence only:

> The method, perhaps more importantly, does not require labeled data.

Revise to:

> The method does not require labeled data.

Unsupported evaluation around a supplied result:

> The method, despite its apparent simplicity, achieves a surprisingly strong
> 84.2% accuracy on Dataset A.

Revise to:

> The method achieves 84.2% accuracy on Dataset A.

Useful content trapped inside an interruption:

> The model, which uses two encoder layers, requires 18% less memory than the
> baseline.

Either keep the relative clause or integrate it when that improves the local flow:

> The two-layer model requires 18% less memory than the baseline.

Necessary scientific qualifiers:

> Under the no-overlap assumption, the estimator is unbiased.

> The treatment increased the score by 2.4 points (95% CI, 1.1 to 3.7).

Preserve both. The first limits the claim; the second carries supplied uncertainty.

## Audit consequence, not rhythm

- Use P2 when an insertion adds only cadence or decorative emphasis.
- Use P1 when it introduces unsupported evaluation, interpretation, or claim
  framing.
- Treat a repair as P0 evidence drift if it removes a condition, uncertainty
  statement, citation, definition, or other information that changes the claim.

Consider repetition across a paragraph or manuscript, but do not produce an
AI-likeness score or infer authorship from phrase density. A deterministic checker
may flag newly introduced high-confidence phrases as review leads; semantic
inspection decides whether to delete, integrate, or preserve them.
