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
