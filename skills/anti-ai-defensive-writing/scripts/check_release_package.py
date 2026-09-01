#!/usr/bin/env python3
"""Audit deterministic identity and packaging surfaces in a paper release bundle."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Iterable, List, Sequence


TEXT_EXTENSIONS = {
    ".bib",
    ".cfg",
    ".cls",
    ".csv",
    ".html",
    ".htm",
    ".ini",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".sty",
    ".svg",
    ".tex",
    ".toml",
    ".ts",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"Dockerfile", "LICENSE", "Makefile", "README"}
VISUAL_EXTENSIONS = {
    ".bmp",
    ".eps",
    ".gif",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".ps",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
}
MEDIA_EXTENSIONS = {".avi", ".mov", ".mp4", ".mpeg", ".mpg", ".webm"}
ARCHIVE_EXTENSIONS = {".7z", ".gz", ".rar", ".tar", ".tgz", ".zip"}
OFFICE_EXTENSIONS = {".docx", ".odp", ".ods", ".odt", ".pptx", ".xlsx"}
SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
}
RESIDUE_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
MAX_SCAN_BYTES = 20 * 1024 * 1024

EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I)
ORCID_RE = re.compile(r"\b(?:https?://orcid\.org/)?\d{4}-\d{4}-\d{4}-[\dX]{4}\b", re.I)
LOCAL_PATH_RE = re.compile(
    r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Z]:\\Users\\[^\\\s]+)", re.I
)
IDENTIFYING_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)/[^\s}\])>,]+",
    re.I,
)
AUTHOR_FIELD_RE = re.compile(
    r"\\(?:author|affiliation|institute|address|authorrunning)\*?"
    r"(?:\s*\[[^\]]*\])?\s*\{(?P<value>[^{}]*)\}",
    re.I,
)
ACKNOWLEDGEMENT_RE = re.compile(
    r"(?:\\begin\{acks\}|\\(?:sub)*section\*?\s*\{\s*acknowledg|"
    r"\backnowledg(?:e)?ments?\b|\bfunded by\b|\bgrant (?:number|no\.?))",
    re.I,
)
ANONYMOUS_VALUE_RE = re.compile(
    r"^\s*(?:anonymous(?: authors?)?|authors? withheld(?: for review)?|redacted|"
    r"paper\s*(?:#|no\.?)?\s*[A-Za-z0-9-]+|"
    r"submission\s*(?:#|no\.?)?\s*[A-Za-z0-9-]+)\s*$",
    re.I,
)
REVIEW_PLACEHOLDER_RE = re.compile(
    r"\b(?:anonymous authors?|authors? withheld(?: for (?:anonymous |blind )?review)?|"
    r"omitted for (?:anonymous |double-blind |blind )?review|"
    r"withheld for (?:anonymous |double-blind |blind )?review|"
    r"redacted for (?:anonymous |double-blind |blind )?review)\b",
    re.I,
)
ANONYMOUS_URL_RE = re.compile(
    r"https?://[^\s}\])>,]*(?:anonymous|anonymized|anon-github)[^\s}\])>,]*",
    re.I,
)
PDF_METADATA_PATTERNS = (
    re.compile(rb"/Author\s*\((?P<value>[^)]{1,500})\)", re.I),
    re.compile(rb"<pdf:Author>(?P<value>.*?)</pdf:Author>", re.I | re.S),
    re.compile(
        rb"<dc:creator>.*?<rdf:li[^>]*>(?P<value>.*?)</rdf:li>.*?</dc:creator>",
        re.I | re.S,
    ),
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class ManualCheck:
    code: str
    message: str
    path: str | None = None


@dataclass
class CheckResult:
    release: str
    anonymity: str | None
    findings: List[Finding]
    manual_checks: List[ManualCheck]
    files_scanned: int

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
            "release": self.release,
            "anonymity": self.anonymity,
            "files_scanned": self.files_scanned,
            "counts": counts,
            "findings": [asdict(item) for item in self.findings],
            "manual_checks": [asdict(item) for item in self.manual_checks],
        }


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in TEXT_NAMES


def _iter_files(
    package: Path,
) -> tuple[List[Path], List[Finding], List[ManualCheck]]:
    findings: List[Finding] = []
    manual_checks: List[ManualCheck] = []
    if package.is_file():
        return [package.resolve()], findings, manual_checks
    files: List[Path] = []
    for root, directories, names in os.walk(package, followlinks=False):
        root_path = Path(root)
        retained = []
        for name in sorted(directories):
            candidate = root_path / name
            if candidate.is_symlink():
                findings.append(
                    Finding(
                        "P1",
                        "package-symlink",
                        "Directory symlink is not followed; verify the uploaded archive target",
                        str(candidate.resolve(strict=False)),
                    )
                )
                continue
            if name in SKIP_DIRECTORIES:
                findings.append(
                    Finding(
                        "P2",
                        "package-residue-directory",
                        "Version-control, dependency, or cache directory is inside the package",
                        str(candidate.resolve()),
                    )
                )
                continue
            retained.append(name)
        directories[:] = retained
        for name in sorted(names):
            candidate = root_path / name
            if candidate.is_symlink():
                findings.append(
                    Finding(
                        "P1",
                        "package-symlink",
                        "File symlink is not followed; verify the uploaded archive target",
                        str(candidate.resolve(strict=False)),
                    )
                )
                continue
            if candidate.is_file():
                files.append(candidate.resolve())
                if name in RESIDUE_FILES:
                    findings.append(
                        Finding(
                            "P2",
                            "package-residue-file",
                            "Operating-system metadata file is inside the package",
                            str(candidate.resolve()),
                        )
                    )
    return files, findings, manual_checks


def _identity_matches(value: str, identity_terms: Sequence[str]) -> Iterable[str]:
    folded = value.casefold()
    for term in identity_terms:
        if term.casefold() in folded:
            yield term


def _path_identity_matches(value: str, identity_terms: Sequence[str]) -> Iterable[str]:
    folded = value.casefold()
    normalized_value = re.sub(r"[^a-z0-9]+", " ", folded).strip()
    for term in identity_terms:
        normalized_term = re.sub(r"[^a-z0-9]+", " ", term.casefold()).strip()
        if term.casefold() in folded or (
            normalized_term and normalized_term in normalized_value
        ):
            yield term


def _scan_text(
    path: Path,
    text: str,
    *,
    release: str,
    anonymity: str | None,
    identity_terms: Sequence[str],
) -> List[Finding]:
    findings: List[Finding] = []

    def add(severity: str, code: str, message: str, match: re.Match[str]) -> None:
        findings.append(
            Finding(severity, code, message, str(path), _line_number(text, match.start()))
        )

    if release == "review" and anonymity == "double-blind":
        for term in _identity_matches(text, identity_terms):
            index = text.casefold().find(term.casefold())
            severity = "P1"
            code = (
                "identity-term-in-bibliography"
                if path.suffix.lower() == ".bib"
                else "identity-term-in-text"
            )
            findings.append(
                Finding(
                    severity,
                    code,
                    f"Supplied identity term appears in readable text: {term!r}",
                    str(path),
                    _line_number(text, index),
                )
            )
        if path.suffix.lower() != ".bib":
            for match in EMAIL_RE.finditer(text):
                add("P0", "possible-email-identity", "Email address appears in review text", match)
            for match in ORCID_RE.finditer(text):
                add("P0", "possible-orcid-identity", "ORCID appears in review text", match)
            for match in LOCAL_PATH_RE.finditer(text):
                add("P0", "local-user-path", "Local home-directory path may identify a user", match)
        for match in AUTHOR_FIELD_RE.finditer(text):
            value = match.group("value").strip()
            if value and not ANONYMOUS_VALUE_RE.search(value):
                add(
                    "P0",
                    "nonanonymous-author-field",
                    "LaTeX author or affiliation field is not visibly anonymized",
                    match,
                )
        for match in ACKNOWLEDGEMENT_RE.finditer(text):
            add(
                "P1",
                "review-acknowledgement-or-funding",
                "Acknowledgement or funding text may be identifying; apply the venue policy",
                match,
            )
        for match in IDENTIFYING_URL_RE.finditer(text):
            add(
                "P1",
                "review-repository-url",
                "Repository URL may reveal identity; verify its anonymity and venue compliance",
                match,
            )
    elif release == "publication":
        for match in AUTHOR_FIELD_RE.finditer(text):
            if ANONYMOUS_VALUE_RE.fullmatch(match.group("value").strip()):
                add(
                    "P1",
                    "review-placeholder-in-publication",
                    "LaTeX author or affiliation field still contains a review-only placeholder",
                    match,
                )
        for match in REVIEW_PLACEHOLDER_RE.finditer(text):
            add(
                "P1",
                "review-placeholder-in-publication",
                "Review-only anonymity placeholder remains in the publication package",
                match,
            )
        for match in ANONYMOUS_URL_RE.finditer(text):
            add(
                "P1",
                "anonymous-url-in-publication",
                "An anonymous review URL remains in the publication package",
                match,
            )
    return findings


def _scan_pdf_metadata(
    path: Path,
    data: bytes,
    *,
    release: str,
    anonymity: str | None,
) -> List[Finding]:
    findings: List[Finding] = []
    for pattern in PDF_METADATA_PATTERNS:
        for match in pattern.finditer(data):
            value = re.sub(rb"\s+", b" ", match.group("value")).strip()
            decoded = value.decode("utf-8", errors="replace")
            if not decoded:
                continue
            if release == "review" and anonymity == "double-blind":
                if not ANONYMOUS_VALUE_RE.search(decoded):
                    findings.append(
                        Finding(
                            "P0",
                            "pdf-author-metadata",
                            f"PDF author metadata is not visibly anonymized: {decoded!r}",
                            str(path),
                        )
                    )
            elif release == "publication" and (
                REVIEW_PLACEHOLDER_RE.search(decoded)
                or ANONYMOUS_VALUE_RE.fullmatch(decoded)
            ):
                findings.append(
                    Finding(
                        "P1",
                        "pdf-review-placeholder",
                        "PDF author metadata still contains a review-only placeholder",
                        str(path),
                    )
                )
    return findings


def check_release_package(
    package: Path,
    *,
    release: str,
    anonymity: str | None = None,
    identity_terms: Sequence[str] = (),
) -> CheckResult:
    package = package.expanduser().resolve()
    if not package.exists():
        raise ValueError(f"Package path does not exist: {package}")
    if release not in {"review", "publication"}:
        raise ValueError("release must be review or publication")
    if release == "review" and anonymity not in {"none", "single-blind", "double-blind"}:
        raise ValueError("review packages require --anonymity none, single-blind, or double-blind")
    if release == "publication" and anonymity is not None:
        raise ValueError("publication packages do not use --anonymity")
    normalized_terms = tuple(dict.fromkeys(term.strip() for term in identity_terms if term.strip()))

    files, findings, manual_checks = _iter_files(package)
    if release == "review":
        manual_checks.append(
            ManualCheck(
                "venue-policy-review",
                "Verify the selected anonymity mode and every policy-dependent disclosure against the current venue rules",
                str(package),
            )
        )
    else:
        manual_checks.append(
            ManualCheck(
                "publication-identity-completeness",
                "Verify final author order, affiliations, acknowledgements, funding, links, and rights against authoritative records",
                str(package),
            )
        )

    for path in files:
        relative = str(path.relative_to(package)) if package.is_dir() else path.name
        if release == "review" and anonymity == "double-blind":
            for term in _path_identity_matches(relative, normalized_terms):
                findings.append(
                    Finding(
                        "P0",
                        "identity-term-in-path",
                        f"Supplied identity term appears in a package path: {term!r}",
                        str(path),
                    )
                )
        suffix = path.suffix.lower()
        try:
            size = path.stat().st_size
        except OSError as exc:
            findings.append(
                Finding("P1", "file-stat-error", f"Cannot inspect file metadata: {exc}", str(path))
            )
            continue
        if suffix in VISUAL_EXTENSIONS or suffix in MEDIA_EXTENSIONS:
            manual_checks.append(
                ManualCheck(
                    "visual-identity-review",
                    "Inspect visible names, usernames, avatars, account UI, paths, comments, watermarks, and participant or annotator identity",
                    str(path),
                )
            )
        if suffix in ARCHIVE_EXTENSIONS:
            manual_checks.append(
                ManualCheck(
                    "archive-content-review",
                    "Inspect archive contents, internal paths, hidden files, and nested metadata",
                    str(path),
                )
            )
        if suffix in OFFICE_EXTENSIONS:
            manual_checks.append(
                ManualCheck(
                    "office-document-review",
                    "Inspect document properties, comments, tracked changes, embedded media, and visible identity",
                    str(path),
                )
            )
        if size > MAX_SCAN_BYTES:
            manual_checks.append(
                ManualCheck(
                    "large-file-unscanned",
                    f"File exceeds the {MAX_SCAN_BYTES // (1024 * 1024)} MiB deterministic scan limit",
                    str(path),
                )
            )
            continue
        if _is_text_file(path):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                findings.append(
                    Finding("P1", "file-read-error", f"Cannot read text file: {exc}", str(path))
                )
            else:
                findings.extend(
                    _scan_text(
                        path,
                        text,
                        release=release,
                        anonymity=anonymity,
                        identity_terms=normalized_terms,
                    )
                )
        if suffix == ".pdf":
            try:
                data = path.read_bytes()
            except OSError as exc:
                findings.append(
                    Finding("P1", "file-read-error", f"Cannot read PDF metadata: {exc}", str(path))
                )
            else:
                findings.extend(
                    _scan_pdf_metadata(
                        path,
                        data,
                        release=release,
                        anonymity=anonymity,
                    )
                )

    severity_rank = {"P0": 0, "P1": 1, "P2": 2}
    findings.sort(
        key=lambda item: (severity_rank[item.severity], item.path or "", item.line or 0, item.code)
    )
    manual_checks.sort(key=lambda item: (item.path or "", item.code))
    return CheckResult(release, anonymity, findings, manual_checks, len(files))


def _format_text(result: CheckResult) -> str:
    profile = result.release
    if result.anonymity:
        profile += f" / {result.anonymity}"
    lines = [f"Release profile: {profile}", f"Files scanned: {result.files_scanned}"]
    if not result.findings:
        lines.append("OK: no deterministic release-package findings")
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
    if result.manual_checks:
        lines.append("Manual verification required:")
        for item in result.manual_checks:
            location = f"{item.path}: " if item.path else ""
            lines.append(f"- {location}{item.code}: {item.message}")
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Exact file or directory intended for upload")
    parser.add_argument(
        "--release",
        choices=("review", "publication"),
        required=True,
        help="Review package or final publication package",
    )
    parser.add_argument(
        "--anonymity",
        choices=("none", "single-blind", "double-blind"),
        help="Venue review model; required only for a review package",
    )
    parser.add_argument(
        "--identity-term",
        action="append",
        default=[],
        help="Known name, username, affiliation, domain, or path fragment; repeat as needed",
    )
    parser.add_argument("--strict", action="store_true", help="Treat P1 and P2 findings as failures")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args(argv)
    try:
        result = check_release_package(
            args.package,
            release=args.release,
            anonymity=args.anonymity,
            identity_terms=args.identity_term,
        )
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result.to_dict(), indent=2) if args.json else _format_text(result))
    return 1 if result.errors or (args.strict and result.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
