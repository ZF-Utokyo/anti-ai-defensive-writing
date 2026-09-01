import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "anti-ai-defensive-writing" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from verify_bibliography_online import (  # noqa: E402
    CROSSREF_WORKS,
    DBLP_PUBLICATIONS,
    LookupFailure,
    ReferenceRecord,
    verify_records,
)


def crossref_item(
    *,
    title="Evidence-Aligned Writing",
    authors=("Jane Smith",),
    year=2024,
    venue="Journal of Clear Results",
    doi="10.1234/example.1",
):
    return {
        "DOI": doi,
        "title": [title],
        "author": [
            {
                "given": " ".join(name.split()[:-1]),
                "family": name.split()[-1],
            }
            for name in authors
        ],
        "published": {"date-parts": [[year]]},
        "container-title": [venue],
        "URL": f"https://doi.org/{doi}",
    }


def dblp_hit(
    *,
    title="Attention Is All You Need.",
    authors=("Ashish Vaswani", "Noam Shazeer"),
    year="2017",
    venue="NIPS",
    url="https://dblp.org/rec/conf/nips/example",
):
    return {
        "info": {
            "title": title,
            "authors": {
                "author": [{"text": name} for name in authors],
            },
            "year": year,
            "venue": venue,
            "url": url,
        }
    }


class OnlineBibliographyVerificationChecks(unittest.TestCase):
    def test_crossref_doi_match_is_verified(self):
        record = ReferenceRecord(
            key="smith2024",
            title="Evidence-Aligned Writing",
            authors=("Smith, Jane",),
            year=2024,
            venue="Journal of Clear Results",
            doi="10.1234/example.1",
            entry_type="article",
        )

        def fetch(url, params, timeout, user_agent):
            self.assertIn("10.1234%2Fexample.1", url)
            return {"message": crossref_item()}

        result = verify_records(
            [record],
            provider="crossref",
            workers=1,
            fetch_json=fetch,
        )[0]
        self.assertEqual("verified", result.status)
        self.assertEqual("crossref", result.provider)
        self.assertEqual("https://doi.org/10.1234/example.1", result.source_url)

    def test_doi_match_with_incomplete_authors_is_conflicting(self):
        record = ReferenceRecord(
            key="paper",
            title="Attention Is All You Need",
            authors=("Vaswani, Ashish", "Shazeer, Noam"),
            year=2018,
            venue="Advances in Neural Information Processing Systems",
            doi="10.1234/attention",
            entry_type="inproceedings",
        )

        def fetch(url, params, timeout, user_agent):
            return {
                "message": crossref_item(
                    title="Attention Is All You Need",
                    authors=(
                        "Ashish Vaswani",
                        "Noam Shazeer",
                        "Niki Parmar",
                    ),
                    year=2017,
                    venue="Advances in Neural Information Processing Systems",
                    doi="10.1234/attention",
                )
            }

        result = verify_records(
            [record],
            provider="crossref",
            workers=1,
            fetch_json=fetch,
        )[0]
        self.assertEqual("conflicting_metadata", result.status)
        self.assertTrue(any("incomplete" in item for item in result.differences))
        self.assertTrue(any("year differs" in item for item in result.differences))

    def test_auto_falls_back_to_dblp_and_prefers_published_record(self):
        record = ReferenceRecord(
            key="vaswani2017",
            title="Attention Is All You Need",
            authors=(
                "Vaswani, Ashish",
                "Shazeer, Noam",
                "Parmar, Niki",
                "Uszkoreit, Jakob",
                "Jones, Llion",
                "Gomez, Aidan N.",
                "Kaiser, Lukasz",
                "Polosukhin, Illia",
            ),
            year=2017,
            venue="NIPS",
            entry_type="inproceedings",
        )
        calls = []

        def fetch(url, params, timeout, user_agent):
            calls.append(url)
            if url == CROSSREF_WORKS:
                return {
                    "message": {
                        "items": [
                            crossref_item(title="Is Attention All You Need?", year=2025)
                        ]
                    }
                }
            self.assertEqual(DBLP_PUBLICATIONS, url)
            authors = (
                "Ashish Vaswani",
                "Noam Shazeer",
                "Niki Parmar",
                "Jakob Uszkoreit",
                "Llion Jones",
                "Aidan N. Gomez",
                "Lukasz Kaiser",
                "Illia Polosukhin",
            )
            return {
                "result": {
                    "hits": {
                        "hit": [
                            dblp_hit(authors=authors, venue="NIPS"),
                            dblp_hit(
                                authors=authors,
                                venue="CoRR",
                                url="https://dblp.org/rec/journals/corr/example",
                            ),
                        ]
                    }
                }
            }

        result = verify_records(
            [record],
            provider="auto",
            workers=1,
            fetch_json=fetch,
        )[0]
        self.assertEqual([CROSSREF_WORKS, DBLP_PUBLICATIONS], calls)
        self.assertEqual("verified", result.status)
        self.assertEqual("dblp", result.provider)
        self.assertIn("/conf/", result.source_url)

    def test_near_candidates_are_ambiguous_not_verified(self):
        record = ReferenceRecord(
            key="query",
            title="Exact Target Title",
            authors=("Doe, Jane",),
            year=2024,
        )

        def fetch(url, params, timeout, user_agent):
            return {
                "message": {
                    "items": [
                        crossref_item(
                            title="A Similar Target Title",
                            doi="10.1234/similar",
                        )
                    ]
                }
            }

        result = verify_records(
            [record],
            provider="crossref",
            workers=1,
            fetch_json=fetch,
        )[0]
        self.assertEqual("ambiguous", result.status)
        self.assertIn("none has the same normalized title", result.message)
        self.assertEqual(("https://doi.org/10.1234/similar",), result.candidate_urls)

    def test_multiple_exact_records_remain_ambiguous(self):
        record = ReferenceRecord(
            key="edition",
            title="Shared Title",
            authors=("Doe, Jane",),
            year=2024,
            entry_type="article",
        )

        def fetch(url, params, timeout, user_agent):
            return {
                "message": {
                    "items": [
                        crossref_item(
                            title="Shared Title",
                            doi="10.1234/one",
                            venue="Journal One",
                        ),
                        crossref_item(
                            title="Shared Title",
                            doi="10.1234/two",
                            venue="Journal Two",
                        ),
                    ]
                }
            }

        result = verify_records(
            [record],
            provider="crossref",
            workers=1,
            fetch_json=fetch,
        )[0]
        self.assertEqual("ambiguous", result.status)
        self.assertEqual(2, len(result.candidate_urls))

    def test_provider_failure_is_reported_without_guessing(self):
        record = ReferenceRecord(key="paper", title="A Paper")

        def fetch(url, params, timeout, user_agent):
            raise LookupFailure("temporary outage")

        result = verify_records(
            [record],
            provider="crossref",
            workers=1,
            fetch_json=fetch,
        )[0]
        self.assertEqual("provider_error", result.status)
        self.assertIn("temporary outage", result.message)

    def test_invalid_configuration_fails_before_network(self):
        record = ReferenceRecord(key="paper", title="A Paper")
        with self.assertRaisesRegex(ValueError, "valid contact email"):
            verify_records([record], mailto="not-an-email")
        with self.assertRaisesRegex(ValueError, "provider"):
            verify_records([record], provider="unknown")


if __name__ == "__main__":
    unittest.main()
