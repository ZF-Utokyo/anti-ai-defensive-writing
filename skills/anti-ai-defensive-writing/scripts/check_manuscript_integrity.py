#!/usr/bin/env python3
"""Check LaTeX cross-references, BibTeX keys, displays, and acronym consistency."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import Iterable, List, Sequence

from verify_bibliography_online import (
    ReferenceRecord,
    VerificationResult,
    verify_records,
)


INCLUDE_RE = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^{}]+)\}")
REFERENCE_RE = re.compile(
    r"\\(?:ref|eqref|autoref|pageref|cref|Cref|subref|vref|Vref)"
    r"\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}"
)
REFERENCE_RANGE_RE = re.compile(
    r"\\(?:crefrange|Crefrange|cpagerefrange|vpagerefrange)"
    r"\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}\s*\{([^{}]+)\}"
)
CITATION_RE = re.compile(
    r"\\(?:cite\w*|parencite|textcite|autocite|footcite|supercite|smartcite|nocite)"
    r"\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}"
)
DISPLAY_RE = re.compile(
    r"\\begin\{(?P<environment>figure\*?|table\*?)\}(?P<body>.*?)"
    r"\\end\{(?P=environment)\}",
    re.S,
)
CAPTION_RE = re.compile(r"\\caption\*?(?:\[[^\]]*\])?\s*\{")
BIBLIOGRAPHY_RE = re.compile(r"\\bibliography\s*\{([^{}]+)\}")
ADD_BIB_RESOURCE_RE = re.compile(
    r"\\addbibresource\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}"
)
BIBITEM_RE = re.compile(r"\\bibitem\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}")
HARDCODED_DISPLAY_RE = re.compile(
    r"(?<![\\\w])(?:Figures?|Figs?|Tables?)\.?\s*~?\s*\d+[A-Za-z]?\b",
    re.I,
)
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9-]{1,9}s?\b")
ACRONYM_DEFINITION_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9/,+\- ]{2,100}\s*\((?P<acronym>[A-Z][A-Z0-9-]{1,9}s?)\)"
)
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
URL_RE = re.compile(r"^https?://\S+$", re.I)

KNOWN_ACRONYMS = {
    "API",
    "ASCII",
    "BibTeX",
    "CPU",
    "DOI",
    "GPU",
    "HTML",
    "HTTP",
    "HTTPS",
    "ISBN",
    "ISSN",
    "LaTeX",
    "ORCID",
    "PDF",
    "URL",
    "UTF",
    "XML",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


@dataclass
class CheckResult:
    findings: List[Finding]
    online_results: List[VerificationResult] = field(default_factory=list)

    @property
    def errors(self) -> List[Finding]:
        return [item for item in self.findings if item.severity == "P0"]

    @property
    def warnings(self) -> List[Finding]:
        return [item for item in self.findings if item.severity != "P0"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        counts = {severity: 0 for severity in ("P0", "P1", "P2")}
        for item in self.findings:
            counts[item.severity] += 1
        return {
            "ok": self.ok,
            "counts": counts,
            "findings": [asdict(item) for item in self.findings],
            "online_verification": [item.to_dict() for item in self.online_results],
        }


@dataclass(frozen=True)
class SourceSpan:
    start: int
    end: int
    path: Path
    source_start: int


@dataclass
class Manuscript:
    text: str
    spans: List[SourceSpan]
    source_texts: dict[Path, str]
    findings: List[Finding]

    def location(self, index: int) -> tuple[str | None, int | None]:
        if not self.spans:
            return None, None
        starts = [span.start for span in self.spans]
        position = bisect_right(starts, index) - 1
        if position < 0:
            return None, None
        span = self.spans[position]
        if index >= span.end:
            return str(span.path), None
        source_index = span.source_start + index - span.start
        raw = self.source_texts[span.path]
        return str(span.path), raw.count("\n", 0, source_index) + 1


@dataclass(frozen=True)
class Display:
    kind: str
    start: int
    end: int
    labels: tuple[str, ...]


@dataclass(frozen=True)
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]
    path: Path
    line: int


def _strip_comments(text: str) -> str:
    """Replace LaTeX comments with spaces while preserving indexes and newlines."""
    output = list(text)
    line_start = 0
    while line_start < len(text):
        line_end = text.find("\n", line_start)
        if line_end < 0:
            line_end = len(text)
        for index in range(line_start, line_end):
            if text[index] != "%":
                continue
            slash_count = 0
            cursor = index - 1
            while cursor >= line_start and text[cursor] == "\\":
                slash_count += 1
                cursor -= 1
            if slash_count % 2 == 0:
                output[index:line_end] = " " * (line_end - index)
                break
        line_start = line_end + 1
    return "".join(output)


class _ManuscriptLoader:
    def __init__(self) -> None:
        self.parts: List[str] = []
        self.spans: List[SourceSpan] = []
        self.source_texts: dict[Path, str] = {}
        self.findings: List[Finding] = []
        self.length = 0

    def _add_finding(
        self, severity: str, code: str, message: str, path: Path, raw: str, index: int
    ) -> None:
        self.findings.append(
            Finding(severity, code, message, str(path), raw.count("\n", 0, index) + 1)
        )

    def _append(self, path: Path, source_start: int, value: str) -> None:
        if not value:
            return
        start = self.length
        self.parts.append(value)
        self.length += len(value)
        self.spans.append(SourceSpan(start, self.length, path, source_start))

    def _append_separator(self) -> None:
        self.parts.append("\n")
        self.length += 1

    def load(self, path: Path, stack: tuple[Path, ...] = ()) -> None:
        path = path.resolve()
        if path in stack:
            chain = " -> ".join(item.name for item in (*stack, path))
            self.findings.append(
                Finding("P0", "include-cycle", f"LaTeX include cycle: {chain}", str(path), 1)
            )
            return
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            self.findings.append(
                Finding("P0", "input-file-error", f"Cannot read LaTeX input: {exc}", str(path), None)
            )
            return

        self.source_texts[path] = raw
        text = _strip_comments(raw)
        cursor = 0
        for match in INCLUDE_RE.finditer(text):
            self._append(path, cursor, text[cursor : match.start()])
            target_text = match.group(1).strip()
            if "\\" in target_text or "#" in target_text:
                self._add_finding(
                    "P1",
                    "dynamic-include",
                    f"Cannot resolve dynamic include: {target_text!r}",
                    path,
                    raw,
                    match.start(),
                )
            else:
                target = path.parent / target_text
                if not target.suffix:
                    target = target.with_suffix(".tex")
                if target.is_file():
                    self._append_separator()
                    self.load(target, (*stack, path))
                    self._append_separator()
                else:
                    self._add_finding(
                        "P0",
                        "missing-include",
                        f"Included LaTeX file does not exist: {target}",
                        path,
                        raw,
                        match.start(),
                    )
            cursor = match.end()
        self._append(path, cursor, text[cursor:])

    def result(self) -> Manuscript:
        return Manuscript(
            text="".join(self.parts),
            spans=self.spans,
            source_texts=self.source_texts,
            findings=self.findings,
        )


def _keys(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _inside(index: int, ranges: Iterable[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in ranges)


def _clean_bib_value(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and (
        (value[0] == "{" and value[-1] == "}")
        or (value[0] == '"' and value[-1] == '"')
    ):
        value = value[1:-1].strip()
    return re.sub(r"\s+", " ", value)


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int | None:
    depth = 1
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"' and depth == 1:
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
    return None


def _parse_bib_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    cursor = 0
    while cursor < len(body):
        match = re.search(r"([A-Za-z][\w-]*)\s*=\s*", body[cursor:])
        if not match:
            break
        name = match.group(1).lower()
        value_start = cursor + match.end()
        if value_start >= len(body):
            break
        opening = body[value_start]
        if opening in '{"':
            closing = "}" if opening == "{" else '"'
            if opening == "{":
                end = _balanced_end(body, value_start + 1, opening, closing)
            else:
                end = value_start + 1
                escaped = False
                while end < len(body):
                    char = body[end]
                    if char == '"' and not escaped:
                        break
                    escaped = char == "\\" and not escaped
                    if char != "\\":
                        escaped = False
                    end += 1
            if end is None or end >= len(body):
                value = body[value_start:]
                cursor = len(body)
            else:
                value = body[value_start : end + 1]
                cursor = end + 1
        else:
            end = body.find(",", value_start)
            if end < 0:
                end = len(body)
            value = body[value_start:end]
            cursor = end
        fields[name] = _clean_bib_value(value)
        comma = body.find(",", cursor)
        cursor = len(body) if comma < 0 else comma + 1
    return fields


def _parse_bib_file(path: Path) -> tuple[List[BibEntry], List[Finding]]:
    findings: List[Finding] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [Finding("P0", "bib-file-error", f"Cannot read BibTeX file: {exc}", str(path), None)]
    text = _strip_comments(raw)
    entries: List[BibEntry] = []
    for match in re.finditer(r"@([A-Za-z]+)\s*([({])", text):
        entry_type = match.group(1).lower()
        if entry_type in {"comment", "preamble", "string"}:
            continue
        opening = match.group(2)
        closing = "}" if opening == "{" else ")"
        end = _balanced_end(text, match.end(), opening, closing)
        line = raw.count("\n", 0, match.start()) + 1
        if end is None:
            findings.append(
                Finding("P0", "malformed-bib-entry", "Unclosed BibTeX entry", str(path), line)
            )
            continue
        content = text[match.end() : end]
        comma = content.find(",")
        if comma < 0:
            findings.append(
                Finding("P0", "malformed-bib-entry", "BibTeX entry has no key separator", str(path), line)
            )
            continue
        key = content[:comma].strip()
        if not key:
            findings.append(
                Finding("P0", "empty-bib-key", "BibTeX entry has an empty key", str(path), line)
            )
            continue
        entries.append(
            BibEntry(entry_type, key, _parse_bib_fields(content[comma + 1 :]), path, line)
        )
    return entries, findings


def _normalize_doi(value: str) -> str:
    value = _clean_bib_value(value).strip()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I)
    return value.rstrip(".,;)")


def _normalize_title(value: str) -> str:
    value = re.sub(r"\\[A-Za-z]+\*?", " ", value)
    value = value.replace("{", "").replace("}", "")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _bibtex_authors(value: str) -> tuple[str, ...]:
    return tuple(
        _clean_bib_value(item)
        for item in re.split(r"\s+and\s+", value, flags=re.I)
        if _clean_bib_value(item)
    )


def _bibtex_year(fields: dict[str, str]) -> int | None:
    value = fields.get("year") or fields.get("date") or ""
    match = re.search(r"\b\d{4}\b", value)
    return int(match.group(0)) if match else None


def _reference_record(entry: BibEntry) -> ReferenceRecord:
    fields = entry.fields
    venue = (
        fields.get("journal")
        or fields.get("journaltitle")
        or fields.get("booktitle")
        or fields.get("publisher")
        or ""
    )
    doi = _normalize_doi(fields["doi"]) if fields.get("doi") else ""
    return ReferenceRecord(
        key=entry.key,
        title=fields.get("title", ""),
        authors=_bibtex_authors(fields.get("author", "")),
        year=_bibtex_year(fields),
        venue=venue,
        doi=doi,
        entry_type=entry.entry_type,
        path=str(entry.path),
        line=entry.line,
    )


def _prose_for_acronyms(text: str) -> str:
    output = text
    for pattern in (
        CITATION_RE,
        REFERENCE_RANGE_RE,
        REFERENCE_RE,
        LABEL_RE,
        BIBLIOGRAPHY_RE,
        ADD_BIB_RESOURCE_RE,
    ):
        output = pattern.sub(lambda match: " " * len(match.group(0)), output)
    output = re.sub(r"(?s)\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)", lambda m: " " * len(m.group(0)), output)
    output = re.sub(r"(?<![\\$])\$(?!\$).*?(?<!\\)\$", lambda m: " " * len(m.group(0)), output)
    output = re.sub(r"\\[A-Za-z@]+\*?", lambda m: " " * len(m.group(0)), output)
    return output


def check_manuscript(
    tex_path: Path,
    *,
    bib_paths: Sequence[Path] = (),
    known_acronyms: Sequence[str] = (),
    report_unused_bib: bool = True,
    verify_online: bool = False,
    verify_all_bib: bool = False,
    online_provider: str = "auto",
    online_mailto: str | None = None,
    online_timeout: float = 10.0,
    online_workers: int = 3,
    online_fetch_json=None,
) -> CheckResult:
    loader = _ManuscriptLoader()
    loader.load(tex_path)
    manuscript = loader.result()
    findings = list(manuscript.findings)
    text = manuscript.text

    def add(severity: str, code: str, message: str, index: int | None = None) -> None:
        path, line = manuscript.location(index) if index is not None else (None, None)
        findings.append(Finding(severity, code, message, path, line))

    labels: dict[str, List[int]] = {}
    for match in LABEL_RE.finditer(text):
        for key in _keys(match.group(1)):
            labels.setdefault(key, []).append(match.start())
    for key, positions in labels.items():
        if len(positions) > 1:
            add("P0", "duplicate-label", f"LaTeX label is defined more than once: {key}", positions[1])

    references: List[tuple[str, int]] = []
    for match in REFERENCE_RE.finditer(text):
        for key in _keys(match.group(1)):
            references.append((key, match.start()))
            if key not in labels:
                add("P0", "undefined-reference", f"Reference has no matching label: {key}", match.start())
    for match in REFERENCE_RANGE_RE.finditer(text):
        for group in (match.group(1), match.group(2)):
            for key in _keys(group):
                references.append((key, match.start()))
                if key not in labels:
                    add("P0", "undefined-reference", f"Reference has no matching label: {key}", match.start())

    displays: List[Display] = []
    for match in DISPLAY_RE.finditer(text):
        environment = match.group("environment")
        kind = "figure" if environment.startswith("figure") else "table"
        body = match.group("body")
        display_labels = tuple(item.group(1).strip() for item in LABEL_RE.finditer(body))
        displays.append(Display(kind, match.start(), match.end(), display_labels))
        if not display_labels:
            add("P1", "display-missing-label", f"{kind.title()} environment has no label", match.start())
        if not CAPTION_RE.search(body):
            add("P1", "display-missing-caption", f"{kind.title()} environment has no caption", match.start())

    display_ranges = [(item.start, item.end) for item in displays]
    external_references = [item for item in references if not _inside(item[1], display_ranges)]
    referenced_labels = {key for key, _ in external_references}
    for display in displays:
        if not display.labels:
            continue
        cited = [key for key in display.labels if key in referenced_labels]
        primary = display.labels[0]
        if not cited:
            add("P1", "uncited-display", f"{display.kind.title()} is never cited in the manuscript: {primary}", display.start)
            continue
        uncited_labels = [key for key in display.labels if key not in referenced_labels]
        if uncited_labels:
            add(
                "P2",
                "unreferenced-display-label",
                f"{display.kind.title()} contains labels that are never referenced: {', '.join(uncited_labels)}",
                display.start,
            )
        first_reference = min(
            position for key, position in external_references if key in display.labels
        )
        if first_reference > display.start:
            add(
                "P1",
                "display-before-first-citation",
                f"{display.kind.title()} appears in source before its first citation: {primary}",
                display.start,
            )

    for kind in ("figure", "table"):
        ordered = [item for item in displays if item.kind == kind and item.labels]
        rank = {id(item): index for index, item in enumerate(ordered)}
        first_mentions: List[tuple[int, Display]] = []
        for display in ordered:
            positions = [pos for key, pos in external_references if key in display.labels]
            if positions:
                first_mentions.append((min(positions), display))
        first_mentions.sort(key=lambda item: item[0])
        ranks = [rank[id(display)] for _, display in first_mentions]
        if ranks != sorted(ranks):
            sequence = ", ".join(display.labels[0] for _, display in first_mentions)
            add(
                "P1",
                "display-citation-order",
                f"{kind.title()} first-citation order differs from source numbering order: {sequence}",
                first_mentions[0][0],
            )

    for match in HARDCODED_DISPLAY_RE.finditer(text):
        if not _inside(match.start(), display_ranges):
            add(
                "P2",
                "hard-coded-display-number",
                f"Use a LaTeX reference command instead of a hard-coded display number: {match.group(0)!r}",
                match.start(),
            )

    citations: List[tuple[str, int]] = []
    has_nocite_all = False
    for match in CITATION_RE.finditer(text):
        keys = _keys(match.group(1))
        if "*" in keys:
            has_nocite_all = True
        citations.extend((key, match.start()) for key in keys if key != "*")

    resolved_bib_paths: List[Path] = []
    if bib_paths:
        resolved_bib_paths.extend(path.expanduser().resolve() for path in bib_paths)
    else:
        for pattern, add_suffix in ((ADD_BIB_RESOURCE_RE, False), (BIBLIOGRAPHY_RE, True)):
            for match in pattern.finditer(text):
                source_path, _ = manuscript.location(match.start())
                base = Path(source_path).parent if source_path else tex_path.resolve().parent
                for value in _keys(match.group(1)):
                    candidate = base / value
                    if add_suffix and not candidate.suffix:
                        candidate = candidate.with_suffix(".bib")
                    resolved_bib_paths.append(candidate.resolve())
    resolved_bib_paths = list(dict.fromkeys(resolved_bib_paths))

    entries: List[BibEntry] = []
    for path in resolved_bib_paths:
        parsed, bib_findings = _parse_bib_file(path)
        entries.extend(parsed)
        findings.extend(bib_findings)
    inline_keys = [key for match in BIBITEM_RE.finditer(text) for key in _keys(match.group(1))]

    entry_positions: dict[str, List[BibEntry]] = {}
    for entry in entries:
        entry_positions.setdefault(entry.key, []).append(entry)
    for key, duplicates in entry_positions.items():
        if len(duplicates) > 1:
            item = duplicates[1]
            findings.append(
                Finding("P0", "duplicate-bib-key", f"BibTeX key is defined more than once: {key}", str(item.path), item.line)
            )

    available_citations = set(entry_positions) | set(inline_keys)
    if citations and not resolved_bib_paths and not inline_keys:
        add(
            "P1",
            "bibliography-source-missing",
            "Citations were found, but no BibTeX resource or inline bibliography could be resolved",
            citations[0][1],
        )
    elif resolved_bib_paths or inline_keys:
        for key, position in citations:
            if key not in available_citations:
                add("P0", "undefined-citation", f"Citation key is missing from the bibliography: {key}", position)

    cited_keys = {key for key, _ in citations}
    if report_unused_bib and entries and not has_nocite_all:
        unused = sorted(set(entry_positions) - cited_keys)
        if unused:
            preview = ", ".join(unused[:12])
            if len(unused) > 12:
                preview += f", ... ({len(unused)} total)"
            item = entry_positions[unused[0]][0]
            findings.append(
                Finding("P2", "unused-bib-entry", f"Bibliography entries are not cited: {preview}", str(item.path), item.line)
            )

    doi_entries: dict[str, List[BibEntry]] = {}
    title_entries: dict[str, List[BibEntry]] = {}
    for entry in entries:
        fields = entry.fields
        required = ["title"]
        if entry.entry_type in {
            "article",
            "inproceedings",
            "conference",
            "incollection",
            "inbook",
            "phdthesis",
            "mastersthesis",
            "techreport",
        }:
            required.append("author")
        for field in required:
            if not fields.get(field):
                findings.append(
                    Finding("P1", "bib-missing-field", f"{entry.key} is missing required field: {field}", str(entry.path), entry.line)
                )
        if entry.entry_type not in {"misc", "online", "software", "dataset"} and not (
            fields.get("year") or fields.get("date")
        ):
            findings.append(
                Finding("P1", "bib-missing-field", f"{entry.key} is missing year or date", str(entry.path), entry.line)
            )
        venue_fields = {
            "article": ("journal", "journaltitle"),
            "inproceedings": ("booktitle",),
            "conference": ("booktitle",),
            "incollection": ("booktitle",),
        }.get(entry.entry_type)
        if venue_fields and not any(fields.get(field) for field in venue_fields):
            findings.append(
                Finding("P1", "bib-missing-venue", f"{entry.key} is missing venue metadata ({'/'.join(venue_fields)})", str(entry.path), entry.line)
            )
        if fields.get("doi"):
            doi = _normalize_doi(fields["doi"])
            if not DOI_RE.fullmatch(doi):
                findings.append(
                    Finding("P1", "invalid-doi", f"{entry.key} has an invalid DOI shape: {fields['doi']!r}", str(entry.path), entry.line)
                )
            else:
                doi_entries.setdefault(doi.lower(), []).append(entry)
        if fields.get("url") and not URL_RE.fullmatch(_clean_bib_value(fields["url"])):
            findings.append(
                Finding("P1", "invalid-url", f"{entry.key} has a non-HTTP(S) URL: {fields['url']!r}", str(entry.path), entry.line)
            )
        title = _normalize_title(fields.get("title", ""))
        if title:
            title_entries.setdefault(title, []).append(entry)

    duplicate_pairs: set[tuple[str, ...]] = set()
    for label, groups in (("DOI", doi_entries), ("normalized title", title_entries)):
        for duplicates in groups.values():
            if len(duplicates) < 2:
                continue
            pair = tuple(sorted(item.key for item in duplicates))
            if pair in duplicate_pairs:
                continue
            duplicate_pairs.add(pair)
            item = duplicates[1]
            findings.append(
                Finding(
                    "P1",
                    "duplicate-bib-record",
                    f"Possible duplicate bibliography records share the same {label}: {', '.join(pair)}",
                    str(item.path),
                    item.line,
                )
            )

    prose = _prose_for_acronyms(text)
    known = KNOWN_ACRONYMS | {item.strip() for item in known_acronyms if item.strip()}
    definition_positions: dict[str, int] = {}
    for match in ACRONYM_DEFINITION_RE.finditer(prose):
        definition_positions.setdefault(match.group("acronym"), match.start("acronym"))
    occurrences: dict[str, List[int]] = {}
    for match in ACRONYM_RE.finditer(prose):
        occurrences.setdefault(match.group(0), []).append(match.start())
    for acronym, positions in occurrences.items():
        if acronym in known or acronym.rstrip("s") in known:
            continue
        definition = definition_positions.get(acronym)
        if definition is None and len(positions) >= 2:
            add("P1", "undefined-acronym", f"Acronym appears repeatedly without a detected definition: {acronym}", positions[0])
        elif definition is not None and positions[0] < definition:
            add("P1", "acronym-before-definition", f"Acronym is used before its detected definition: {acronym}", positions[0])
        if len(acronym.rstrip("s")) >= 3:
            case_variants = [
                match for match in re.finditer(rf"\b{re.escape(acronym)}\b", prose, re.I)
                if match.group(0) != acronym
            ]
            if case_variants:
                add(
                    "P1",
                    "acronym-case-drift",
                    f"Acronym casing is inconsistent: expected {acronym}, found {case_variants[0].group(0)}",
                    case_variants[0].start(),
                )

    online_results: List[VerificationResult] = []
    if verify_online:
        target_keys = (
            set(entry_positions)
            if verify_all_bib or has_nocite_all
            else cited_keys
        )
        records = [
            _reference_record(items[0])
            for key, items in entry_positions.items()
            if key in target_keys and len(items) == 1
        ]
        if not records:
            add(
                "P1",
                "online-no-records",
                "No unique cited BibTeX records are available for online verification",
            )
        else:
            online_results = verify_records(
                records,
                provider=online_provider,
                mailto=online_mailto,
                timeout=online_timeout,
                workers=online_workers,
                fetch_json=online_fetch_json,
            )
            online_severity = {
                "conflicting_metadata": ("P0", "online-metadata-conflict"),
                "likely_match": ("P1", "online-metadata-review"),
                "ambiguous": ("P1", "online-metadata-ambiguous"),
                "not_found": ("P1", "online-metadata-not-found"),
                "provider_error": ("P1", "online-provider-error"),
                "unverifiable": ("P1", "online-record-unverifiable"),
            }
            for result in online_results:
                if result.status not in online_severity:
                    continue
                severity, code = online_severity[result.status]
                details = "; ".join(result.differences) or result.message
                findings.append(
                    Finding(
                        severity,
                        code,
                        f"{result.key}: {details}",
                        result.path,
                        result.line,
                    )
                )

    severity_rank = {"P0": 0, "P1": 1, "P2": 2}
    findings.sort(key=lambda item: (severity_rank[item.severity], item.path or "", item.line or 0, item.code))
    return CheckResult(findings, online_results)


def _format_text(result: CheckResult) -> str:
    if not result.findings and not result.online_results:
        return "OK: manuscript integrity checks passed"
    lines = [] if result.findings else ["OK: local manuscript integrity checks passed"]
    for severity in ("P0", "P1", "P2"):
        items = [item for item in result.findings if item.severity == severity]
        if not items:
            continue
        lines.append(f"{severity} findings:")
        for item in items:
            location = ""
            if item.path:
                location = item.path + (f":{item.line}" if item.line else "") + ": "
            lines.append(f"- {location}{item.code}: {item.message}")
    if result.online_results:
        lines.append("Online verification:")
        for item in result.online_results:
            provider = f" via {item.provider}" if item.provider else ""
            lines.append(f"- [{item.status}] {item.key}{provider}: {item.message}")
            lines.extend(f"  - {difference}" for difference in item.differences)
            if item.source_url:
                lines.append(f"  - Source: {item.source_url}")
            lines.extend(f"  - Candidate: {url}" for url in item.candidate_urls)
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", type=Path, help="Main LaTeX manuscript file")
    parser.add_argument(
        "--bib",
        action="append",
        default=[],
        type=Path,
        help="BibTeX file; repeat for multiple files (otherwise discover from LaTeX)",
    )
    parser.add_argument(
        "--known-acronym",
        action="append",
        default=[],
        help="Allow a field-standard or venue-exempt acronym; repeat as needed",
    )
    parser.add_argument(
        "--no-unused-bib",
        action="store_true",
        help="Do not report bibliography entries unused by this manuscript",
    )
    parser.add_argument(
        "--verify-online",
        action="store_true",
        help="Verify cited BibTeX metadata through Crossref and DBLP",
    )
    parser.add_argument(
        "--verify-all-bib",
        action="store_true",
        help="Verify every BibTeX entry instead of cited entries only",
    )
    parser.add_argument(
        "--online-provider",
        choices=("auto", "crossref", "dblp"),
        default="auto",
        help="Online metadata provider (default: Crossref with DBLP fallback)",
    )
    parser.add_argument(
        "--mailto",
        help="Contact email for the Crossref polite pool",
    )
    parser.add_argument(
        "--online-timeout",
        type=float,
        default=10.0,
        metavar="SECONDS",
        help="Timeout for each provider request (default: 10)",
    )
    parser.add_argument(
        "--online-workers",
        type=int,
        default=3,
        metavar="N",
        help="Concurrent online lookups, capped at 8 (default: 3)",
    )
    parser.add_argument("--strict", action="store_true", help="Treat P1 and P2 findings as failures")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args(argv)

    try:
        result = check_manuscript(
            args.tex,
            bib_paths=args.bib,
            known_acronyms=args.known_acronym,
            report_unused_bib=not args.no_unused_bib,
            verify_online=args.verify_online,
            verify_all_bib=args.verify_all_bib,
            online_provider=args.online_provider,
            online_mailto=args.mailto,
            online_timeout=args.online_timeout,
            online_workers=args.online_workers,
        )
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result.to_dict(), indent=2) if args.json else _format_text(result))
    return 1 if result.errors or (args.strict and result.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
