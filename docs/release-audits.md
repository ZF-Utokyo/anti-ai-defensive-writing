# Review and publication release audits

Release audits stay inside the Paper workflow. The evidence rules do not change;
the identity and packaging policy changes with the release profile.

## Choose the profile

| Profile | Includes | Identity rule |
| --- | --- | --- |
| Review package | Submission, revision, and resubmission | Use the venue's explicit `none`, `single-blind`, or `double-blind` model |
| Publication package | Accepted and camera-ready material | Restore verified author-facing information and remove review-only placeholders |

The word "submission" does not imply anonymity. A single-blind journal may require
author names in the submitted manuscript. A double-blind conference may forbid
identifying information across the complete bundle.

Use the current official venue instructions. If the venue policy or review model
cannot be verified, report compliance as unresolved instead of guessing.

## Audit the exact upload manifest

Check the files that will actually be uploaded, not only `main.tex` or an unrelated
working repository. Include, when present:

- rendered paper and LaTeX source;
- appendices and supplementary PDFs;
- figures, tables, screenshots, and diagrams;
- code, data, README files, repository links, and artifact instructions;
- videos, slides, response letters, and generated metadata;
- file names, directory names, archive contents, and document properties.

Private Git history and unrelated working files are out of scope unless they are
included in the upload package.

## Review packages

For `none` or `single-blind`, do not remove author information merely because the
paper is being submitted. Apply the venue's actual requirements.

For `double-blind`, check the complete package for:

- author names, affiliations, email, ORCID, biographies, and distinctive lab names;
- acknowledgements, grant identifiers, and funding details;
- personal, institutional, repository, dataset, demo, and project URLs;
- first-person self-identification and public-preprint wording;
- PDF, image, office-document, archive, and media author or creator metadata;
- identifying file and directory names;
- visible names, usernames, avatars, account menus, browser tabs, terminal prompts,
  home-directory paths, comments, and watermarks in screenshots or videos.

Do not delete self-citations automatically. Use the same third-person form as for
other work unless the venue explicitly requires a different treatment.
Acknowledgements, public repositories, preprints, and ethics disclosures are
policy-dependent surfaces, not universal violations.

## Publication packages

Check that the final package contains the authoritative:

- author names, order, affiliations, and contact details;
- acknowledgements and funding;
- repository, dataset, demo, and artifact links;
- venue-required rights and publication statements.

Find review-only residue such as `Anonymous Authors`, `withheld for review`,
anonymous URLs, or redacted acknowledgements. Request missing authoritative values;
do not invent them.

De-anonymizing the authors does not remove participant privacy. Continue checking
screenshots, appendices, samples, logs, and videos for participant, interviewee,
annotator, or staff names, usernames, faces, and other personal data. Reveal those
details only when consent, policy, and the research purpose support disclosure.

## Run the package checker

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  submission/ --release review --anonymity double-blind \
  --identity-term "Author Name"
```

Use repeated `--identity-term` values for specific known names, usernames,
affiliations, domains, project names, email fragments, and path fragments. A surname
alone can collide with a legitimate bibliography entry.

For camera-ready material:

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  camera-ready/ --release publication
```

The checker is offline and read-only. It scans paths, readable text, common LaTeX
identity fields, email, ORCID, repository URLs, local home paths, accessible PDF
author metadata, review placeholders, and package residue.

## Complete the visual pass

The checker inventories PDFs, images, videos, office documents, and archives as
manual checks. Render each submitted PDF and inspect every page. Inspect screenshots
at useful resolution and review slides, videos, and linked artifacts with available
tools.

OCR can identify possible text, but a clean OCR result does not prove that an image
contains no identity. Compressed metadata, archive internals, linked resources, and
unsupported media formats may remain unverified. List them instead of declaring
the package anonymous.

## Report readiness

Separate deterministic findings from manual and visual checks. Conclude with one
of these states:

- **Ready under the supplied policy:** every required surface was checked and no
  blocking issue remains.
- **Not ready:** a policy violation, identity exposure, or missing final field
  remains.
- **Unresolved:** the venue policy or a required visual, metadata, archive, or
  linked-artifact surface could not be verified.

Never claim that a text-only scan proves anonymity.
