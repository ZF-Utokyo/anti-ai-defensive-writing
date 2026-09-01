# Examples

These examples illustrate decisions, not phrases that must be copied.

## Reflexive caveat

Before:

> While these findings are promising, they should be interpreted with caution, and
> we cannot claim that the method consistently improves performance.

Evidence supplied: accuracy increased from 72.1% to 75.4% on Dataset A.

After:

> The method improves accuracy from 72.1% to 75.4% on Dataset A.

The dataset name supplies the relevant boundary. A generic caution paragraph adds
no information.

## Unsupported confidence interval

Request: turn the supplied means into a results table. The user supplies 81.2 and
79.8, with no replicate data or uncertainty estimates.

Wrong:

| Method | Accuracy (95% CI) |
| --- | --- |
| Proposed | 81.2 (80.4-82.0) |

Right:

| Method | Accuracy |
| --- | ---: |
| Proposed | 81.2 |

The interval cannot be inferred from the mean.

## Legitimate confidence interval

Evidence supplied: treatment effect 2.4 points, 95% CI 1.1 to 3.7.

Keep:

> The treatment increased the outcome by 2.4 points (95% CI, 1.1 to 3.7).

The skill removes invented rigor, not valid uncertainty.

## Technical term with a real definition

Source:

> We maximize the SVM margin, defined as the distance between the separating
> hyperplane and the nearest training samples.

Keep it. "Margin" has a defined mathematical role. It is not an AI artifact merely
because models sometimes insert it unnecessarily.

## Undefined probe

Before:

> A static probe confirms that the representation captures stable semantic content.

No probe procedure or result is supplied.

Clean revision:

> The representation captures semantic content on the evaluated classification
> task.

If that claim is also unsupported, request the relevant result instead of inventing
a probe design.

## Abstract noun chain

Before:

> The framework operationalizes a multidimensional lens for interrogating the
> latent structural dynamics of representation quality.

Supplied method: linear classifiers are trained on frozen representations for three
downstream tasks.

After:

> We measure representation quality by training linear classifiers on frozen
> representations for three downstream tasks.

## Exact limitation instead of claim paralysis

Before:

> The results may suggest improved generalization, although no definitive claim can
> be made and performance may vary in other contexts.

Evidence supplied: the method improves all three evaluated out-of-domain datasets.

After:

> The method improves performance on all three evaluated out-of-domain datasets.

This is a strong comparative claim with an explicit evaluated scope. It does not
claim universal generalization.

## Remove an unsupported claim without negating it

Before:

> The result may suggest improved transfer, although it does not establish reliable
> transfer gains.

Evidence supplied: accuracy increases from 72.1% to 75.4% on Dataset A using the
same training data. No transfer evaluation is supplied.

After:

> The method improves accuracy from 72.1% to 75.4% on Dataset A using the same
> training data.

The unsupported transfer claim is unnecessary. Replacing it with a sentence about
what the result cannot establish would preserve the reviewer voice rather than
clean it.
