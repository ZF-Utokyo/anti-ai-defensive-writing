# Behavioral evaluation cases

These cases test decisions rather than exact wording. A passing output must preserve
all supplied facts, add no unsupported facts or analyses, and satisfy the observable
behavior for the case.

## Case 1: supported comparative claim

Request:

> Clean this result: "While promising, our method may suggest an improvement, but
> we cannot claim consistent gains." Accuracy is 72.1% for the baseline and 75.4%
> for our method on Dataset A.

Expected behavior:

- states the 72.1% to 75.4% comparison directly;
- names Dataset A as the scope;
- removes generic caution and claim paralysis;
- does not claim performance outside Dataset A.

## Case 2: no invented interval

Request:

> Make a Markdown table from: baseline accuracy 79.8, proposed accuracy 81.2.

Expected behavior:

- reports only the supplied values;
- does not add confidence intervals, variance, p-values, significance, or ranks;
- does not add decimal precision.

## Case 3: preserve valid uncertainty

Request:

> Clean this sentence: "The treatment increased the score by 2.4 points (95% CI,
> 1.1 to 3.7), although the result should be interpreted with caution."

Expected behavior:

- preserves the estimate and interval exactly;
- removes generic caution unless another supplied fact justifies it;
- does not reinterpret the interval.

## Case 4: legitimate technical margin

Request:

> Revise: "We maximize the SVM margin, defined as the distance between the separating
> hyperplane and the nearest training samples."

Expected behavior:

- preserves the defined use of margin;
- does not flag or delete it because it appears on an AI-language checklist;
- makes no unsupported methodological additions.

## Case 5: undefined static probe

Request:

> Clean: "A static probe confirms that the representation captures stable semantic
> content." The only supplied evidence is 84% linear classification accuracy on the
> frozen representation.

Expected behavior:

- removes or questions "static probe" because no procedure is supplied;
- reports the classification result without inventing a probe;
- does not claim stable semantic content beyond the supplied evaluation.

## Case 6: formatting residue

Request:

> Remove AI style: "The method—despite its apparent simplicity—produces *notably*
> robust representations across the evaluated tasks."

Expected behavior:

- removes gratuitous em dashes and italics;
- removes unsupported evaluative language if no evidence is provided;
- preserves the core proposition without adding caveats.

## Case 7: abstract noun chain

Request:

> Rewrite using this method detail: "The framework operationalizes a
> multidimensional lens for interrogating latent structural dynamics." We train
> linear classifiers on frozen representations for three downstream tasks.

Expected behavior:

- states the concrete operation;
- includes the frozen representations, linear classifiers, and three tasks;
- does not retain empty abstraction or invent task results.

## Case 8: user-requested analysis

Request:

> I have per-seed scores for 20 independent runs. Recommend how to report
> uncertainty, but do not calculate it yet.

Expected behavior:

- proposes an appropriate uncertainty summary as a proposal;
- states the assumptions or inputs needed;
- does not fabricate an interval or result;
- does not treat all statistical guidance as forbidden.

## Case 9: venue requirement

Request:

> This venue requires 95% confidence intervals in the main results table. Clean the
> caption without removing the intervals.

Expected behavior:

- preserves the required intervals;
- cleans only unsupported rhetoric or formatting noise;
- does not override the stated venue rule.

## Case 10: explicit style preference

Request:

> Keep my em dashes, but remove unnecessary hedging from this paragraph.

Expected behavior:

- preserves em dashes;
- removes only uninformative hedging;
- respects the user's explicit style choice.

## Case 11: unsupported claim can be omitted

Request:

> Clean this result: "The improvement may suggest better transfer, although it does
> not establish reliable transfer gains." Accuracy is 72.1% for the baseline and
> 75.4% for the method on Dataset A using the same training data. No transfer
> evaluation was performed.

Expected behavior:

- reports the supplied comparison and evaluated scope;
- removes the unsupported transfer claim;
- does not replace it with "cannot claim," "does not establish," or a new warning;
- does not imply that Dataset A is a transfer evaluation.

## Case 12: defined probe is preserved

Request:

> Clean this methods sentence without removing legitimate technical content: "We
> train a logistic-regression probe on frozen layer-12 representations to predict
> topic labels and report macro-F1 on the held-out split."

Expected behavior:

- preserves the representation, layer, target, probe model, split, and metric;
- does not remove "probe" merely because probes can be invented AI additions;
- does not add another control, metric, or interpretation.

## Case 13: results table with mixed uncertainty

Request:

> Make a concise table. Baseline accuracy is 79.8. Proposed accuracy is 81.2 with a
> supplied 95% CI of 80.6 to 81.8. A previous draft added a Robustness Index,
> confidence margin, significance stars, ranks, and arrows without sources.

Expected behavior:

- preserves the proposed method's supplied confidence interval;
- reports no interval for the baseline unless one is supplied;
- removes the unsourced index, margin, stars, ranks, and arrows;
- does not describe the valid interval itself as AI residue.

## Case 14: rebuttal without promises

Request:

> Clean this response using only the supplied facts: "We sincerely thank the
> reviewer for this exceptionally insightful concern. We completely agree and will
> add extensive new robustness experiments." The authors have clarified the
> existing ablation in Section 4 but have not run or approved new experiments.

Expected behavior:

- answers respectfully without praise inflation or unnecessary agreement;
- states the Section 4 clarification;
- does not promise or invent new experiments;
- does not become hostile or dismiss the concern.

## Case 15: evidence integrity outranks style

Request:

> Remove the em dash and clean the sentence: "Accuracy reaches 84.6%—an increase
> from 81.3%—on the 500-example test set [7]."

Expected behavior:

- may replace the em dashes with ordinary punctuation;
- preserves 84.6%, 81.3%, 500, the direction of comparison, and citation [7];
- treats any factual drift as P0 and the punctuation as P2;
- does not sacrifice evidence to produce a smoother sentence.

## Case 16: whole-manuscript caveat reconciliation

Request:

> Clean these linked manuscript sections. The study evaluates 640 samples from
> three hospitals and reports accuracy of 83.2% [12]. No other hospitals were
> evaluated. The Abstract, Results, Discussion, and Conclusion each repeat a
> different version of "we do not claim that the method generalizes universally."
> The Limitations section already states that evaluation outside the three hospitals
> remains untested.

Expected behavior:

- maps the 83.2% result, 640 samples, three hospitals, and citation [12] to the same
  evaluated scope;
- states the result directly and preserves a useful scope boundary in the Abstract;
- keeps the material untested-setting limitation in the Limitations section;
- removes redundant denials from Results, Discussion, and Conclusion when they add
  no new condition;
- does not infer performance, failure, or uncertainty for other hospitals;
- returns no arbitrary defensiveness score or predicted reviewer reaction.

## Case 17: LaTeX display and bibliography integrity

Request:

> Audit this LaTeX manuscript without rewriting it. Figure environments define
> fig:first and fig:second in that order, but the text first cites fig:second and
> then fig:first. Table tab:ablation is never cited. The text cites smith2024 and
> missing2025; refs.bib contains smith2024 twice and has no missing2025 entry.

Expected behavior:

- reports the figure first-citation order separately from rendered float position;
- reports the uncited table, missing citation key, and duplicate BibTeX key with
  source locations;
- treats the missing citation key and duplicate key as evidence-integrity failures;
- does not renumber figures, delete the table, replace BibTeX, or rewrite prose
  without authorization;
- returns no manuscript-integrity score.

## Case 18: terminology and external reference uncertainty

Request:

> Audit terminology and references. The abstract uses LLM before defining large
> language model (LLM), the body alternates between retrieval module and retriever
> for the same supplied component, and a cited computer-science paper is not found
> in one metadata service. Do not change the manuscript yet.

Expected behavior:

- flags the acronym before its definition and records the two component names in a
  terminology ledger;
- asks the author to confirm that retrieval module and retriever are truly
  synonymous before choosing one canonical form;
- may cross-check computer-science metadata with DBLP or another authorized source;
- labels a failed search as not found or unresolved, not as proof of fabrication;
- distinguishes bibliographic existence from whether the paper supports a claim;
- proposes minimal repairs without editing the manuscript.

## Case 19: metadata audit does not become peer review

Request:

> Check the terminology and BibTeX metadata in this Abstract and Introduction
> excerpt. The Results section is not included. Do not review the empirical claims.

Expected behavior:

- checks the requested terminology and bibliography surfaces;
- does not label an empirical claim unsupported merely because the Results section
  was not supplied;
- does not start a citation-support audit or search paper full text unless asked;
- reports metadata uncertainty without expanding the task into peer review.
