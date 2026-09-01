# Paper release packages

Use this workflow when the user asks whether a submission, revision, resubmission,
camera-ready paper, appendix, or supplementary package is ready to upload. Keep it
inside the Paper path. The writing and evidence rules stay shared; the release
profile changes identity and packaging checks.

## Contents

- Select the release profile
- Build the upload manifest
- Audit a review package
- Audit a publication package
- Combine deterministic and visual checks
- Return release findings

## Select the release profile

Choose one profile before auditing:

- **Review package:** a submission, revision, or resubmission sent for review. Set
  anonymity to `none`, `single-blind`, or `double-blind` from the venue policy.
- **Publication package:** an accepted or camera-ready release. Restore required
  author-facing information and remove review-only placeholders.

Do not infer the review model from the word "submission." Ask for the venue policy
or use the user's stated review model. If neither is available, scan for possible
exposures but label venue compliance unresolved. A venue's current instructions
override generic conventions.

If the user names a venue but does not supply its policy, consult the current
official author or submission instructions when web access is available and record
the access date. Do not rely on an old template, a remembered rule, or a third-party
summary when the official policy is available.

## Build the upload manifest

Audit the exact files that will be uploaded, not only the main manuscript or the
working repository. Record each artifact, its audience, identity surfaces, policy
rule, observed evidence, and status. Include, when present:

- the rendered paper and source archive;
- appendices and supplementary PDFs;
- figures, tables, screenshots, and diagrams;
- code, data, README files, anonymous repositories, and artifact links;
- videos, slides, response letters, and generated metadata;
- file names, directory names, document properties, and archive contents.

Do not audit private repository history or unrelated working files unless they are
part of the upload package. Report hidden files, version-control directories, or
build residue found inside the actual package.

## Audit a review package

For `none` or `single-blind`, do not remove author information merely because it is
a submission. Confirm only the requirements stated by the venue.

For `double-blind`, inspect every artifact for:

- author names, affiliations, email addresses, ORCID identifiers, biographies,
  acknowledgements, grant identifiers, and distinctive laboratory names;
- personal, institutional, repository, dataset, demo, and project URLs;
- first-person self-identification, public preprint wording, and non-anonymous
  artifact instructions;
- author or creator fields in PDF, image, office-document, archive, and media
  metadata;
- names, usernames, avatars, browser tabs, terminal prompts, home-directory paths,
  comments, watermarks, and account menus inside screenshots or videos;
- identifying file names and directory paths in the upload archive.

Do not delete self-citations by default. Cite the authors' prior work in the same
third-person form as other work unless the venue explicitly requires another form.
Treat acknowledgements, public repositories, supplementary links, preprints, and
ethics disclosures as policy-dependent rather than applying one universal rule.

## Audit a publication package

Check that the final package contains the verified author names, order,
affiliations, contact details, acknowledgements, funding, repository or artifact
links, and rights statements required by the venue. Find review-only residue such
as `Anonymous Authors`, `withheld for review`, anonymous URLs, or redacted
acknowledgements. Do not invent missing identity or funding information; request
the authoritative values.

De-anonymizing the authors does not remove privacy obligations. Continue checking
screenshots, appendices, data samples, logs, and videos for participant,
interviewee, annotator, or staff names, usernames, faces, and other personal data.
Keep or reveal those details only when consent, policy, and research needs support
it.

## Combine deterministic and visual checks

Run the read-only package checker on the exact upload directory:

    python3 scripts/check_release_package.py submission/ \
      --release review --anonymity double-blind \
      --identity-term "Author Name" \
      --identity-term "github.com/author-account"

Use repeated `--identity-term` values for known names, usernames, affiliations,
project names, domains, email fragments, and local path fragments. Prefer specific
terms; a surname alone can collide with a legitimate bibliography entry.
Collect these terms from user-supplied author records or explicit instructions. If
they are unavailable, run the generic scan and mark name-specific coverage
unresolved rather than searching unrelated private files for identity clues.

For a camera-ready package:

    python3 scripts/check_release_package.py camera-ready/ --release publication

The checker scans file and directory names, readable text, common LaTeX identity
fields, review placeholders, repository URLs, local paths, and accessible PDF
metadata. It inventories visual and media artifacts for manual inspection. It does
not perform OCR, understand venue rules, inspect compressed metadata reliably, or
certify anonymity.

Render every submitted PDF and inspect every page. Inspect raster images at useful
resolution and review videos or slides when tools permit. OCR can produce leads,
but a clean OCR result is not proof that a screenshot contains no name. If visual
inspection is unavailable, list the unverified artifacts instead of declaring the
package safe.

## Return release findings

Report the release profile and supplied policy first. For each consequential
finding, give severity, artifact and location, observed identity surface, applicable
policy, and smallest repair. Keep deterministic findings separate from manual or
visual checks. End with one of:

- **ready under the supplied policy**, only when all required surfaces were checked;
- **not ready**, when a blocking exposure or missing final field remains;
- **unresolved**, when the venue policy or a visual, metadata, archive, or linked
  artifact could not be verified.

Never claim that a text-only scan proves anonymity.
