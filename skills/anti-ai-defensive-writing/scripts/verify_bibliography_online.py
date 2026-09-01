#!/usr/bin/env python3
"""Verify bibliography metadata with documented Crossref and DBLP APIs."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
import html
import json
import re
import unicodedata
from typing import Callable, List, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


CROSSREF_WORKS = "https://api.crossref.org/works"
DBLP_PUBLICATIONS = "https://dblp.org/search/publ/api"
PROJECT_URL = "https://github.com/ZF-Utokyo/anti-ai-defensive-writing"
USER_AGENT = f"anti-ai-defensive-writing/0.3.0 ({PROJECT_URL})"


class LookupNotFound(Exception):
    """A provider returned a valid not-found response."""


class LookupFailure(Exception):
    """A provider request could not be completed."""


FetchJSON = Callable[[str, Mapping[str, str], float, str], dict]


@dataclass(frozen=True)
class ReferenceRecord:
    key: str
    title: str = ""
    authors: tuple[str, ...] = ()
    year: int | None = None
    venue: str = ""
    doi: str = ""
    entry_type: str = ""
    path: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class ProviderCandidate:
    provider: str
    title: str
    authors: tuple[str, ...]
    year: int | None
    venue: str
    doi: str
    url: str


@dataclass(frozen=True)
class VerificationResult:
    key: str
    status: str
    provider: str | None
    message: str
    source_url: str | None = None
    differences: tuple[str, ...] = ()
    candidate_urls: tuple[str, ...] = ()
    path: str | None = None
    line: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _fetch_json(
    url: str, params: Mapping[str, str], timeout: float, user_agent: str
) -> dict:
    query = urlencode(params)
    target = f"{url}?{query}" if query else url
    request = Request(
        target,
        headers={
            "Accept": "application/json",
            "User-Agent": user_agent,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise LookupNotFound from exc
        raise LookupFailure(f"HTTP {exc.code}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LookupFailure(str(exc)) from exc


def _first(value: object) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value) if value is not None else ""


def _integer(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _crossref_year(item: Mapping[str, object]) -> int | None:
    for key in ("published-print", "published-online", "published", "issued"):
        value = item.get(key)
        if not isinstance(value, Mapping):
            continue
        parts = value.get("date-parts")
        if (
            isinstance(parts, list)
            and parts
            and isinstance(parts[0], list)
            and parts[0]
        ):
            year = _integer(parts[0][0])
            if year is not None:
                return year
    return None


def _crossref_candidate(item: Mapping[str, object]) -> ProviderCandidate:
    authors = []
    raw_authors = item.get("author")
    if isinstance(raw_authors, list):
        for author in raw_authors:
            if not isinstance(author, Mapping):
                continue
            name = " ".join(
                part for part in (str(author.get("given", "")).strip(), str(author.get("family", "")).strip())
                if part
            )
            if name:
                authors.append(name)
    doi = str(item.get("DOI", "")).strip()
    source_url = str(item.get("URL", "")).strip()
    if not source_url and doi:
        source_url = f"https://doi.org/{quote(doi, safe='/')}"
    return ProviderCandidate(
        provider="crossref",
        title=html.unescape(_first(item.get("title"))).strip(),
        authors=tuple(authors),
        year=_crossref_year(item),
        venue=html.unescape(_first(item.get("container-title"))).strip(),
        doi=doi,
        url=source_url,
    )


def _crossref_lookup(
    record: ReferenceRecord,
    *,
    mailto: str | None,
    timeout: float,
    fetch_json: FetchJSON,
) -> List[ProviderCandidate]:
    params = {"mailto": mailto} if mailto else {}
    if record.doi:
        url = f"{CROSSREF_WORKS}/{quote(record.doi, safe='')}"
        payload = fetch_json(url, params, timeout, USER_AGENT)
        message = payload.get("message")
        return [_crossref_candidate(message)] if isinstance(message, Mapping) else []

    query_parts = [record.title]
    if record.authors:
        query_parts.append(record.authors[0])
    if record.year is not None:
        query_parts.append(str(record.year))
    params.update(
        {
            "query.bibliographic": " ".join(part for part in query_parts if part),
            "rows": "5",
            "select": "DOI,title,author,published,container-title,URL,type",
        }
    )
    payload = fetch_json(CROSSREF_WORKS, params, timeout, USER_AGENT)
    message = payload.get("message")
    items = message.get("items") if isinstance(message, Mapping) else None
    if not isinstance(items, list):
        return []
    return [_crossref_candidate(item) for item in items if isinstance(item, Mapping)]


def _dblp_authors(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ()
    authors = value.get("author")
    if isinstance(authors, Mapping):
        authors = [authors]
    if not isinstance(authors, list):
        return ()
    names = []
    for author in authors:
        if isinstance(author, Mapping):
            name = str(author.get("text", "")).strip()
        else:
            name = str(author).strip()
        name = re.sub(r"\s+\d{4}$", "", html.unescape(name))
        if name:
            names.append(name)
    return tuple(names)


def _dblp_candidate(info: Mapping[str, object]) -> ProviderCandidate:
    doi = str(info.get("doi", "")).strip()
    return ProviderCandidate(
        provider="dblp",
        title=html.unescape(str(info.get("title", ""))).strip().rstrip("."),
        authors=_dblp_authors(info.get("authors")),
        year=_integer(info.get("year")),
        venue=html.unescape(str(info.get("venue", ""))).strip(),
        doi=doi,
        url=str(info.get("url", "")).strip()
        or (f"https://doi.org/{quote(doi, safe='/')}" if doi else ""),
    )


def _surname(name: str) -> str:
    value = re.sub(r"[{}]", "", name).strip()
    if "," in value:
        value = value.split(",", 1)[0]
    else:
        parts = value.split()
        value = parts[-1] if parts else ""
    return _normalize_text(value)


def _dblp_lookup(
    record: ReferenceRecord,
    *,
    timeout: float,
    fetch_json: FetchJSON,
) -> List[ProviderCandidate]:
    query_parts = []
    if record.authors:
        family = _surname(record.authors[0])
        if family:
            query_parts.append(family)
    query_parts.append(record.title)
    params = {
        "q": " ".join(part for part in query_parts if part),
        "format": "json",
        "h": "10",
        "c": "0",
    }
    payload = fetch_json(DBLP_PUBLICATIONS, params, timeout, USER_AGENT)
    result = payload.get("result")
    hits_container = result.get("hits") if isinstance(result, Mapping) else None
    hits = hits_container.get("hit") if isinstance(hits_container, Mapping) else None
    if isinstance(hits, Mapping):
        hits = [hits]
    if not isinstance(hits, list):
        return []
    candidates = []
    for hit in hits:
        info = hit.get("info") if isinstance(hit, Mapping) else None
        if isinstance(info, Mapping):
            candidates.append(_dblp_candidate(info))
    return candidates


def _normalize_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"\\[A-Za-z]+\*?", " ", value)
    value = value.replace("{", "").replace("}", "")
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(char if char.isalnum() else " " for char in value)
    return re.sub(r"\s+", " ", value).strip()


def _author_surnames(authors: Sequence[str]) -> tuple[str, ...]:
    return tuple(value for value in (_surname(author) for author in authors) if value)


def _venue_kind(value: str) -> str:
    normalized = _normalize_text(value)
    if normalized in {"corr", "arxiv"} or normalized.startswith("arxiv "):
        return "preprint"
    return "published"


def _narrow_exact_candidates(
    record: ReferenceRecord, candidates: Sequence[ProviderCandidate]
) -> List[ProviderCandidate]:
    exact = [
        candidate
        for candidate in candidates
        if record.title
        and _normalize_text(candidate.title) == _normalize_text(record.title)
    ]
    if len(exact) <= 1:
        return exact

    if record.year is not None:
        same_year = [candidate for candidate in exact if candidate.year == record.year]
        if same_year:
            exact = same_year
    supplied_authors = set(_author_surnames(record.authors))
    if supplied_authors and len(exact) > 1:
        matching_authors = [
            candidate
            for candidate in exact
            if supplied_authors.issubset(set(_author_surnames(candidate.authors)))
        ]
        if matching_authors:
            exact = matching_authors
    if record.entry_type in {"inproceedings", "conference", "article"} and len(exact) > 1:
        published = [
            candidate for candidate in exact if _venue_kind(candidate.venue) == "published"
        ]
        if published:
            exact = published
    return exact


def _compare(
    record: ReferenceRecord, candidate: ProviderCandidate
) -> tuple[str, tuple[str, ...]]:
    differences = []
    conflicts = []
    soft_differences = []

    if record.doi and candidate.doi and record.doi.casefold() != candidate.doi.casefold():
        value = f"DOI differs: supplied {record.doi}; source {candidate.doi}"
        differences.append(value)
        conflicts.append(value)
    if record.title and _normalize_text(record.title) != _normalize_text(candidate.title):
        value = f"title differs: supplied {record.title!r}; source {candidate.title!r}"
        differences.append(value)
        conflicts.append(value)

    supplied_authors = set(_author_surnames(record.authors))
    source_authors = set(_author_surnames(candidate.authors))
    if supplied_authors and source_authors and supplied_authors != source_authors:
        if supplied_authors.issubset(source_authors):
            missing = [
                author
                for author in candidate.authors
                if _surname(author) not in supplied_authors
            ]
            value = "author list is incomplete; source also lists " + ", ".join(missing)
        else:
            value = (
                "author list differs: supplied "
                + ", ".join(record.authors)
                + "; source "
                + ", ".join(candidate.authors)
            )
        differences.append(value)
        conflicts.append(value)
    elif not supplied_authors or not source_authors:
        value = "author metadata could not be compared completely"
        differences.append(value)
        soft_differences.append(value)

    if record.year is not None and candidate.year is not None and record.year != candidate.year:
        value = f"year differs: supplied {record.year}; source {candidate.year}"
        differences.append(value)
        if abs(record.year - candidate.year) <= 1:
            soft_differences.append(value)
        else:
            conflicts.append(value)
    elif record.year is None or candidate.year is None:
        value = "year metadata could not be compared completely"
        differences.append(value)
        soft_differences.append(value)

    if (
        record.venue
        and candidate.venue
        and _normalize_text(record.venue) != _normalize_text(candidate.venue)
    ):
        value = f"venue differs or uses an alias: supplied {record.venue!r}; source {candidate.venue!r}"
        differences.append(value)
        soft_differences.append(value)

    if conflicts:
        return "conflicting_metadata", tuple(differences)
    if soft_differences:
        return "likely_match", tuple(differences)
    return "verified", ()


def _result_from_candidates(
    record: ReferenceRecord,
    provider: str,
    candidates: Sequence[ProviderCandidate],
) -> VerificationResult:
    if record.doi and provider == "crossref" and candidates:
        chosen = candidates[0]
        status, differences = _compare(record, chosen)
        return VerificationResult(
            key=record.key,
            status=status,
            provider=provider,
            message="Matched by DOI" if status == "verified" else "DOI matched; review field differences",
            source_url=chosen.url or None,
            differences=differences,
            path=record.path,
            line=record.line,
        )

    exact = _narrow_exact_candidates(record, candidates)
    if len(exact) == 1:
        chosen = exact[0]
        status, differences = _compare(record, chosen)
        return VerificationResult(
            key=record.key,
            status=status,
            provider=provider,
            message="Matched by normalized title" if status == "verified" else "Title matched; review field differences",
            source_url=chosen.url or None,
            differences=differences,
            path=record.path,
            line=record.line,
        )
    if len(exact) > 1:
        urls = tuple(candidate.url for candidate in exact if candidate.url)
        return VerificationResult(
            key=record.key,
            status="ambiguous",
            provider=provider,
            message="Multiple exact-title records remain after author, year, and venue checks",
            candidate_urls=urls[:5],
            path=record.path,
            line=record.line,
        )
    near_urls = tuple(candidate.url for candidate in candidates if candidate.url)
    return VerificationResult(
        key=record.key,
        status="ambiguous" if near_urls else "not_found",
        provider=provider,
        message=(
            "Provider returned candidates, but none has the same normalized title"
            if near_urls
            else "Provider returned no candidate"
        ),
        candidate_urls=near_urls[:5],
        path=record.path,
        line=record.line,
    )


def _verify_one(
    record: ReferenceRecord,
    *,
    provider: str,
    mailto: str | None,
    timeout: float,
    fetch_json: FetchJSON,
) -> VerificationResult:
    if not record.title and not record.doi:
        return VerificationResult(
            key=record.key,
            status="unverifiable",
            provider=None,
            message="The entry has neither a title nor a DOI",
            path=record.path,
            line=record.line,
        )

    providers = [provider] if provider != "auto" else ["crossref", "dblp"]
    fallback: VerificationResult | None = None
    failures = []
    for current in providers:
        try:
            if current == "crossref":
                candidates = _crossref_lookup(
                    record,
                    mailto=mailto,
                    timeout=timeout,
                    fetch_json=fetch_json,
                )
            else:
                candidates = _dblp_lookup(
                    record,
                    timeout=timeout,
                    fetch_json=fetch_json,
                )
        except LookupNotFound:
            result = VerificationResult(
                key=record.key,
                status="not_found",
                provider=current,
                message="Provider has no record for the supplied identifier",
                path=record.path,
                line=record.line,
            )
        except LookupFailure as exc:
            failures.append(f"{current}: {exc}")
            continue
        else:
            result = _result_from_candidates(record, current, candidates)

        if result.status in {"verified", "likely_match", "conflicting_metadata"}:
            return result
        if fallback is None or result.status == "ambiguous":
            fallback = result

    if fallback is not None:
        return fallback
    return VerificationResult(
        key=record.key,
        status="provider_error",
        provider=provider,
        message="; ".join(failures) if failures else "No provider could be queried",
        path=record.path,
        line=record.line,
    )


def verify_records(
    records: Sequence[ReferenceRecord],
    *,
    provider: str = "auto",
    mailto: str | None = None,
    timeout: float = 10.0,
    workers: int = 3,
    fetch_json: FetchJSON | None = None,
) -> List[VerificationResult]:
    """Verify records concurrently while preserving input order."""
    if provider not in {"auto", "crossref", "dblp"}:
        raise ValueError("provider must be auto, crossref, or dblp")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if mailto and ("@" not in mailto or any(char.isspace() for char in mailto)):
        raise ValueError("mailto must be a valid contact email")
    worker_count = min(max(int(workers), 1), 8)
    fetch = fetch_json or _fetch_json

    def run(record: ReferenceRecord) -> VerificationResult:
        return _verify_one(
            record,
            provider=provider,
            mailto=mailto,
            timeout=timeout,
            fetch_json=fetch,
        )

    if worker_count == 1 or len(records) <= 1:
        return [run(record) for record in records]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(run, records))
