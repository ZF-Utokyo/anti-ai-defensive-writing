#!/usr/bin/env python3
"""Check an academic rewrite for evidence drift and invented analytical machinery."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Iterable, List, Sequence


NUMBER_RE = re.compile(
    r"(?<![\w.])[+\-\u2212]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"(?:[eE][+\-]?\d+)?(?:\s*%)?"
)
LATEX_REFERENCE_RE = re.compile(
    r"\\(?:cite\w*|ref|eqref|autoref|label)\s*(?:\[[^\]]*\]\s*)*\{[^{}]+\}"
)
BRACKET_CITATION_RE = re.compile(r"\[(?:\d+(?:\s*[-\u2013,]\s*\d+)*)\]")
URL_RE = re.compile(r"https?://[^\s<>()\]]+")
CODE_BLOCK_RE = re.compile(r"(?ms)^(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^(?P=fence)\s*$")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+")
WORD_RE = re.compile(r"\b[\w'-]+\b")

MATH_PATTERNS = (
    re.compile(r"(?s)\$\$.*?\$\$"),
    re.compile(r"(?s)\\\[.*?\\\]"),
    re.compile(r"(?s)\\\(.*?\\\)"),
    re.compile(r"(?<![\\$])\$(?!\$|\s)[^$\n]+?(?<![\\\s])\$(?!\$)"),
)

ANALYTICAL_PATTERNS = {
    "confidence interval": re.compile(r"\b(?:confidence interval|\d+\s*%\s*CI)\b", re.I),
    "p-value": re.compile(r"\bp\s*[- ]?value\b", re.I),
    "effect size": re.compile(r"\beffect size\b", re.I),
    "bootstrap analysis": re.compile(r"\bbootstrap(?:ped|ping)?\b", re.I),
    "significance claim": re.compile(r"\bstatistical(?:ly)? significant\b", re.I),
    "standard error": re.compile(r"\bstandard error\b", re.I),
    "standard deviation": re.compile(r"\bstandard deviation\b", re.I),
    "probe": re.compile(r"\b(?:linear|static) probe\b", re.I),
    "confidence margin": re.compile(r"\bconfidence margin\b", re.I),
    "robustness construct": re.compile(
        r"\brobustness (?:analysis|check|index|metric|score)\b", re.I
    ),
    "composite metric": re.compile(r"\bcomposite (?:index|metric|score)\b", re.I),
}

DEFENSIVE_PATTERNS = {
    "claim paralysis": re.compile(r"\b(?:we|the authors?) cannot claim\b", re.I),
    "generic caution": re.compile(r"\bshould be interpreted with caution\b", re.I),
    "weak suggestion": re.compile(r"\bmay (?:potentially )?suggest\b", re.I),
    "negative disclaimer": re.compile(r"\bdoes not establish\b", re.I),
    "false concession": re.compile(r"\bwhile (?:these )?(?:results|findings) (?:are )?promising\b", re.I),
    "generic future work": re.compile(r"\bfurther (?:research|work) is needed\b", re.I),
}

RHETORICAL_INSERTION_PATTERNS = {
    "importance aside": re.compile(r"\b(?:perhaps\s+)?more importantly\b", re.I),
    "surprise aside": re.compile(r"\bperhaps more surprisingly\b", re.I),
    "note-taking frame": re.compile(r"\bit is worth noting that\b", re.I),
    "apparent-simplicity aside": re.compile(
        r"\b(?:despite its apparent simplicity|while seemingly simple)\b", re.I
    ),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


@dataclass
class CheckResult:
    errors: List[Finding]
    warnings: List[Finding]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": [asdict(item) for item in self.errors],
            "warnings": [asdict(item) for item in self.warnings],
        }


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _normalize_number(value: str) -> str | None:
    match = NUMBER_RE.fullmatch(value.strip())
    if not match:
        return None
    normalized = match.group(0).replace("\u2212", "-").replace(",", "")
    normalized = re.sub(r"\s+%", "%", normalized)
    return normalized.lower()


def _numbers(text: str) -> Counter:
    values = []
    for match in NUMBER_RE.finditer(text):
        value = _normalize_number(match.group(0))
        if value is not None:
            values.append(value)
    return Counter(values)


def _matches(pattern: re.Pattern, text: str, normalize: bool = True) -> Counter:
    values = []
    for match in pattern.finditer(text):
        value = match.group(0)
        values.append(_normalize_space(value) if normalize else value)
    return Counter(values)


def _math(text: str) -> Counter:
    values = []
    for pattern in MATH_PATTERNS:
        values.extend(_normalize_space(m.group(0)) for m in pattern.finditer(text))
    return Counter(values)


def _counter_message(kind: str, before: Counter, after: Counter) -> str:
    missing = list((before - after).elements())
    added = list((after - before).elements())
    parts = []
    if missing:
        parts.append("missing " + repr(missing))
    if added:
        parts.append("introduced " + repr(added))
    return f"{kind} changed: " + "; ".join(parts)


def _compare_counter(
    errors: List[Finding], code: str, kind: str, before: Counter, after: Counter
) -> None:
    if before != after:
        errors.append(Finding("P0", code, _counter_message(kind, before, after)))


def _introduced_counts(patterns: dict, before: str, after: str) -> Iterable[str]:
    for label, pattern in patterns.items():
        if len(pattern.findall(after)) > len(pattern.findall(before)):
            yield label


def check_rewrite(
    before: str,
    after: str,
    *,
    allow_new_analysis: bool = False,
    allow_structure_change: bool = False,
    allow_drop_numbers: Sequence[str] = (),
) -> CheckResult:
    errors: List[Finding] = []
    warnings: List[Finding] = []

    before_numbers = _numbers(before)
    after_numbers = _numbers(after)
    for requested in allow_drop_numbers:
        normalized = _normalize_number(requested)
        if normalized is None or before_numbers[normalized] == 0:
            errors.append(
                Finding(
                    "P0",
                    "invalid-number-allowance",
                    f"Allowed dropped number is not present in the source: {requested!r}",
                )
            )
            continue
        before_numbers[normalized] -= 1
        if before_numbers[normalized] == 0:
            del before_numbers[normalized]
    _compare_counter(errors, "numeric-drift", "Numeric evidence", before_numbers, after_numbers)
    _compare_counter(
        errors,
        "latex-reference-drift",
        "LaTeX citation/reference commands",
        _matches(LATEX_REFERENCE_RE, before),
        _matches(LATEX_REFERENCE_RE, after),
    )
    _compare_counter(
        errors,
        "bracket-citation-drift",
        "Bracketed numeric citations",
        _matches(BRACKET_CITATION_RE, before),
        _matches(BRACKET_CITATION_RE, after),
    )
    _compare_counter(
        errors,
        "url-drift",
        "URLs",
        _matches(URL_RE, before, normalize=False),
        _matches(URL_RE, after, normalize=False),
    )
    _compare_counter(errors, "math-drift", "Math spans", _math(before), _math(after))
    _compare_counter(
        errors,
        "code-block-drift",
        "Fenced code blocks",
        _matches(CODE_BLOCK_RE, before, normalize=False),
        _matches(CODE_BLOCK_RE, after, normalize=False),
    )

    if not allow_structure_change:
        before_headings = [len(item) for item in HEADING_RE.findall(before)]
        after_headings = [len(item) for item in HEADING_RE.findall(after)]
        if before_headings != after_headings:
            errors.append(
                Finding(
                    "P0",
                    "heading-structure-drift",
                    f"Heading level sequence changed: {before_headings} -> {after_headings}",
                )
            )

    if not allow_new_analysis:
        for label in _introduced_counts(ANALYTICAL_PATTERNS, before, after):
            errors.append(
                Finding(
                    "P0",
                    "introduced-analysis",
                    f"The rewrite introduces an unsourced analytical element: {label}",
                )
            )

    for label in _introduced_counts(DEFENSIVE_PATTERNS, before, after):
        warnings.append(
            Finding(
                "P1",
                "introduced-defensiveness",
                f"The rewrite introduces defensive reviewer voice: {label}",
            )
        )

    for label in _introduced_counts(RHETORICAL_INSERTION_PATTERNS, before, after):
        warnings.append(
            Finding(
                "P2",
                "introduced-rhetorical-insertion",
                "The rewrite introduces a likely cadence filler "
                f"({label}); review whether it adds evidence, scope, or meaning",
            )
        )

    before_words = len(WORD_RE.findall(before))
    after_words = len(WORD_RE.findall(after))
    if before_words >= 50 and after_words < before_words * 0.55:
        warnings.append(
            Finding(
                "P1",
                "large-deletion",
                f"The rewrite retains only {after_words} of {before_words} words; inspect for lost context",
            )
        )

    return CheckResult(errors=errors, warnings=warnings)


def _format_text(result: CheckResult) -> str:
    if result.ok and not result.warnings:
        return "OK: academic rewrite checks passed"
    lines = []
    for heading, items in (("Errors", result.errors), ("Warnings", result.warnings)):
        if items:
            lines.append(f"{heading}:")
            lines.extend(f"- [{item.severity}] {item.code}: {item.message}" for item in items)
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="Original Markdown or text file")
    parser.add_argument("after", type=Path, help="Rewritten Markdown or text file")
    parser.add_argument(
        "--allow-new-analysis",
        action="store_true",
        help="Allow analytical terms intentionally requested by the user",
    )
    parser.add_argument(
        "--allow-structure-change",
        action="store_true",
        help="Allow Markdown heading levels to change",
    )
    parser.add_argument(
        "--allow-drop-number",
        action="append",
        default=[],
        metavar="VALUE",
        help="Allow one explicitly quarantined source number to be removed; repeat as needed",
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args(argv)

    try:
        before = args.before.read_text(encoding="utf-8")
        after = args.after.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    result = check_rewrite(
        before,
        after,
        allow_new_analysis=args.allow_new_analysis,
        allow_structure_change=args.allow_structure_change,
        allow_drop_numbers=args.allow_drop_number,
    )
    print(json.dumps(result.to_dict(), indent=2) if args.json else _format_text(result))
    return 1 if result.errors or (args.strict and result.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
