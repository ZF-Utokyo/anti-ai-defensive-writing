# Evidence and statistical hygiene

Use these rules when the request involves quantitative results, uncertainty,
metrics, experimental design, or claim strength.

## Classify every analytical element

- **Source-backed:** Present in user data, cited material, or verified output.
  Preserve it accurately. Mere appearance in a draft is insufficient when the user
  explicitly identifies the item as an unsourced AI addition.
- **Task-required:** Requested by the user or required by a stated venue or method.
  Include it when the necessary inputs exist.
- **Proposed:** Potentially useful but not supplied or computed. Label it as a
  suggestion and explain what data or procedure it would require.
- **Unsupported:** Neither supplied, required, computed, nor justified. Remove it.

When the user explicitly quarantines a draft value as fabricated, unverified, or
source-free, remove both the construct and its value in Clean mode. Do not repeat it
in a disclaimer. In Audit mode, quote it only to identify the artifact.

Never promote a proposed element into a reported result.

## Confidence intervals and significance

Report a confidence interval, standard error, standard deviation, p-value, effect
size, or significance marker only when at least one of these conditions holds:

- the user supplied it;
- it can be computed from available data and the user asked for the analysis;
- the stated venue or protocol requires it.

Do not generate plausible-looking bounds around a mean. Do not infer sample size,
distribution, independence, or resampling procedure. If a table contains a valid
interval, retain it unless the user asks for a different presentation and no rule
requires it in that table.

## Metrics

Every reported metric needs:

- a name that maps to a defined quantity;
- a stated direction when it is not obvious;
- a calculation or authoritative definition available to the work;
- a reason it informs the paper's claim.

Do not invent composite scores, normalized gains, robustness indices, confidence
margins, or weighted averages to make a result appear more complete. If a new
metric would genuinely help, propose it separately with its definition and inputs.

## Probes, margins, and auxiliary analyses

Terms such as "linear probe," "static probe," "margin," "calibration," and
"robustness check" can be legitimate. Keep or introduce them only when the object,
procedure, data, and interpretive role are clear.

- A probe requires a specified representation, target, model or procedure, and
  evaluation measure.
- A margin requires a mathematical or operational definition.
- A robustness analysis requires a defined perturbation or condition and an outcome.

If the user supplied an undefined term, preserve the underlying result and request
or flag the missing definition. Do not manufacture a conventional-sounding method.

## Claim calibration

Choose the strongest accurate claim type supported by the material:

- **Descriptive:** State what was observed in the evaluated data.
- **Comparative:** State the measured difference under the named conditions.
- **Associational:** State a relationship without causal language.
- **Causal:** Use only when the design supports causal identification.
- **Generalizing:** Extend beyond evaluated settings only when the evidence or study
  design supports that extension.

A boundary should be concrete. Prefer "on the three evaluated datasets" to
"these findings should be interpreted cautiously." Prefer "was associated with"
to a paragraph explaining that causality cannot be claimed.

## When evidence is incomplete

Do one of the following, in order:

1. State the narrower result directly.
2. Ask for the missing value or definition if it blocks the requested output.
3. Mark a new analysis as a recommendation, including the inputs it needs.

Do not fill gaps with invented precision or generalized caution.
