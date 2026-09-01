import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "anti-ai-defensive-writing" / "scripts"
SCRIPT = SCRIPT_DIR / "check_manuscript_integrity.py"
sys.path.insert(0, str(SCRIPT_DIR))

from check_manuscript_integrity import check_manuscript  # noqa: E402


VALID_BIB = """\
@article{smith2024,
  title = {Evidence-Aligned Writing},
  author = {Smith, Jane},
  journal = {Journal of Clear Results},
  year = {2024},
  doi = {10.1234/example.1},
  url = {https://example.org/paper}
}
"""


class ManuscriptIntegrityChecks(unittest.TestCase):
    def codes(self, result):
        return [item.code for item in result.findings]

    def write_project(self, directory, tex, bib=VALID_BIB):
        root = Path(directory)
        main = root / "main.tex"
        main.write_text(tex, encoding="utf-8")
        if bib is not None:
            root.joinpath("refs.bib").write_text(bib, encoding="utf-8")
        return main

    def test_clean_manuscript_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                r"""
We use a large language model (LLM). The LLM produces the draft.
Figure~\ref{fig:pipeline} shows the pipeline.
\begin{figure}
\caption{Pipeline used in the experiment.}
\label{fig:pipeline}
\end{figure}
Table~\ref{tab:results} reports the result.
\begin{table}
\caption{Accuracy on the evaluated dataset.}
\label{tab:results}
\end{table}
Prior work describes the baseline \cite{smith2024}.
\bibliography{refs}
""",
            )
            result = check_manuscript(main)
            self.assertTrue(result.ok)
            self.assertEqual([], result.findings)

    def test_broken_reference_citation_and_duplicate_label_are_p0(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                r"""
See Figure~\ref{fig:missing} and \cite{missing2025}.
\label{dup:key}
\label{dup:key}
\bibliography{refs}
""",
            )
            result = check_manuscript(main)
            self.assertIn("undefined-reference", self.codes(result))
            self.assertIn("undefined-citation", self.codes(result))
            self.assertIn("duplicate-label", self.codes(result))
            self.assertFalse(result.ok)
            self.assertTrue(all(item.severity == "P0" for item in result.errors))

    def test_display_first_citation_order_is_checked_by_type(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                r"""
Figure~\ref{fig:second} is discussed before Figure~\ref{fig:first}.
\begin{figure}
\caption{First source figure.}
\label{fig:first}
\end{figure}
\begin{figure}
\caption{Second source figure.}
\label{fig:second}
\end{figure}
""",
                bib=None,
            )
            result = check_manuscript(main)
            self.assertIn("display-citation-order", self.codes(result))
            self.assertNotIn("uncited-display", self.codes(result))

    def test_panel_and_range_reference_commands_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                r"""
Panels~\subref{fig:panel-a} and Figures~\crefrange{fig:first}{fig:second}
summarize the result.
\begin{figure}
\caption{First figure and panel.}
\label{fig:first}
\label{fig:panel-a}
\end{figure}
\begin{figure}
\caption{Second figure.}
\label{fig:second}
\end{figure}
""",
                bib=None,
            )
            result = check_manuscript(main)
            self.assertNotIn("undefined-reference", self.codes(result))
            self.assertNotIn("uncited-display", self.codes(result))

    def test_display_after_first_citation_and_panel_label_handling(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                r"""
Figure~\ref{fig:main} gives the overview.
\begin{figure}
\caption{Overview with two panels.}
\label{fig:main}
\label{fig:panel-a}
\end{figure}
""",
                bib=None,
            )
            result = check_manuscript(main)
            self.assertIn("unreferenced-display-label", self.codes(result))
            self.assertNotIn("uncited-display", self.codes(result))
            self.assertNotIn("display-before-first-citation", self.codes(result))

    def test_missing_display_metadata_and_hard_coded_number_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                r"""
Figure 1 summarizes the system.
\begin{figure}
Content without structural metadata.
\end{figure}
""",
                bib=None,
            )
            result = check_manuscript(main)
            codes = self.codes(result)
            self.assertIn("hard-coded-display-number", codes)
            self.assertIn("display-missing-label", codes)
            self.assertIn("display-missing-caption", codes)

    def test_static_inputs_are_followed_and_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath("section.tex").write_text(
                r"""
% \ref{commented-out} \cite{not-real}
Figure~\ref{fig:included} is included.
\begin{figure}
\caption{Included figure.}
\label{fig:included}
\end{figure}
The method follows prior work \cite{smith2024}.
""",
                encoding="utf-8",
            )
            main = self.write_project(
                directory,
                "\\input{section}\n\\bibliography{refs}\n",
            )
            result = check_manuscript(main)
            self.assertTrue(result.ok)
            self.assertNotIn("undefined-reference", self.codes(result))
            self.assertNotIn("undefined-citation", self.codes(result))

    def test_finding_location_points_to_included_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            included = root / "section.tex"
            included.write_text(
                "Opening sentence.\nSee Figure~\\ref{fig:missing}.\n",
                encoding="utf-8",
            )
            main = self.write_project(directory, "\\input{section}\n", bib=None)
            result = check_manuscript(main)
            finding = next(
                item for item in result.findings if item.code == "undefined-reference"
            )
            self.assertEqual(str(included.resolve()), finding.path)
            self.assertEqual(2, finding.line)

    def test_bibtex_quality_and_duplicate_records_are_reported(self):
        bib = """\
@article{first,
  title = {Same Paper},
  author = {A. Author},
  journal = {Example Journal},
  year = {2024},
  doi = {bad-doi}
}
@article{second,
  title = {Same Paper},
  year = {2024}
}
@article{second,
  title = {Another Record},
  author = {B. Author},
  journal = {Example Journal},
  year = {2025}
}
"""
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{first,second}\n\\bibliography{refs}\n",
                bib=bib,
            )
            result = check_manuscript(main)
            codes = self.codes(result)
            self.assertIn("duplicate-bib-key", codes)
            self.assertIn("bib-missing-field", codes)
            self.assertIn("bib-missing-venue", codes)
            self.assertIn("invalid-doi", codes)
            self.assertIn("duplicate-bib-record", codes)

    def test_online_verification_is_integrated_with_local_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{smith2024}\n\\bibliography{refs}\n",
            )

            def fetch(url, params, timeout, user_agent):
                return {
                    "message": {
                        "DOI": "10.1234/example.1",
                        "title": ["Evidence-Aligned Writing"],
                        "author": [{"given": "Jane", "family": "Smith"}],
                        "published": {"date-parts": [[2024]]},
                        "container-title": ["Journal of Clear Results"],
                        "URL": "https://doi.org/10.1234/example.1",
                    }
                }

            result = check_manuscript(
                main,
                verify_online=True,
                online_provider="crossref",
                online_workers=1,
                online_fetch_json=fetch,
            )
            self.assertEqual(1, len(result.online_results))
            self.assertEqual("verified", result.online_results[0].status)
            self.assertNotIn("online-metadata-conflict", self.codes(result))
            self.assertEqual(
                "verified",
                result.to_dict()["online_verification"][0]["status"],
            )

    def test_online_metadata_conflict_is_p0(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{smith2024}\n\\bibliography{refs}\n",
            )

            def fetch(url, params, timeout, user_agent):
                return {
                    "message": {
                        "DOI": "10.1234/example.1",
                        "title": ["Different Work"],
                        "author": [{"given": "Alex", "family": "Doe"}],
                        "published": {"date-parts": [[2020]]},
                        "container-title": ["Another Journal"],
                        "URL": "https://doi.org/10.1234/example.1",
                    }
                }

            result = check_manuscript(
                main,
                verify_online=True,
                online_provider="crossref",
                online_workers=1,
                online_fetch_json=fetch,
            )
            self.assertIn("online-metadata-conflict", self.codes(result))
            self.assertFalse(result.ok)

    def test_online_mode_verifies_cited_records_only_by_default(self):
        bib = VALID_BIB + """\
@article{unused2023,
  title = {Unused Work},
  author = {Doe, Alex},
  journal = {Archive},
  year = {2023},
  doi = {10.1234/unused}
}
"""
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{smith2024}\n\\bibliography{refs}\n",
                bib=bib,
            )
            calls = []

            def fetch(url, params, timeout, user_agent):
                calls.append(url)
                return {
                    "message": {
                        "DOI": "10.1234/example.1",
                        "title": ["Evidence-Aligned Writing"],
                        "author": [{"given": "Jane", "family": "Smith"}],
                        "published": {"date-parts": [[2024]]},
                        "container-title": ["Journal of Clear Results"],
                        "URL": "https://doi.org/10.1234/example.1",
                    }
                }

            result = check_manuscript(
                main,
                verify_online=True,
                online_provider="crossref",
                online_workers=1,
                online_fetch_json=fetch,
            )
            self.assertEqual(1, len(calls))
            self.assertEqual(["smith2024"], [item.key for item in result.online_results])

    def test_online_mode_can_verify_the_full_bibliography(self):
        bib = VALID_BIB + """\
@article{unused2023,
  title = {Unused Work},
  author = {Doe, Alex},
  journal = {Archive},
  year = {2023},
  doi = {10.1234/unused}
}
"""
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{smith2024}\n\\bibliography{refs}\n",
                bib=bib,
            )

            def fetch(url, params, timeout, user_agent):
                if "unused" in url:
                    return {
                        "message": {
                            "DOI": "10.1234/unused",
                            "title": ["Unused Work"],
                            "author": [{"given": "Alex", "family": "Doe"}],
                            "published": {"date-parts": [[2023]]},
                            "container-title": ["Archive"],
                            "URL": "https://doi.org/10.1234/unused",
                        }
                    }
                return {
                    "message": {
                        "DOI": "10.1234/example.1",
                        "title": ["Evidence-Aligned Writing"],
                        "author": [{"given": "Jane", "family": "Smith"}],
                        "published": {"date-parts": [[2024]]},
                        "container-title": ["Journal of Clear Results"],
                        "URL": "https://doi.org/10.1234/example.1",
                    }
                }

            result = check_manuscript(
                main,
                verify_online=True,
                verify_all_bib=True,
                online_provider="crossref",
                online_workers=1,
                online_fetch_json=fetch,
            )
            self.assertEqual(
                ["smith2024", "unused2023"],
                [item.key for item in result.online_results],
            )

    def test_unused_bibliography_entries_can_be_suppressed(self):
        bib = VALID_BIB + """\
@article{unused2023,
  title = {Unused Work},
  author = {Doe, Alex},
  journal = {Archive},
  year = {2023}
}
"""
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{smith2024}\n\\bibliography{refs}\n",
                bib=bib,
            )
            reported = check_manuscript(main)
            suppressed = check_manuscript(main, report_unused_bib=False)
            self.assertIn("unused-bib-entry", self.codes(reported))
            self.assertNotIn("unused-bib-entry", self.codes(suppressed))

    def test_nocite_all_suppresses_unused_bibliography_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\nocite{*}\n\\bibliography{refs}\n",
            )
            result = check_manuscript(main)
            self.assertNotIn("unused-bib-entry", self.codes(result))

    def test_inline_bibliography_resolves_citation(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\cite{inline2024}\n\\begin{thebibliography}{1}\n"
                "\\bibitem{inline2024} Entry.\\n\\end{thebibliography}\n",
                bib=None,
            )
            result = check_manuscript(main)
            self.assertNotIn("bibliography-source-missing", self.codes(result))
            self.assertNotIn("undefined-citation", self.codes(result))

    def test_acronym_definition_order_and_case_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                """
LLM output is evaluated. We later define large language model (LLM).
The llm is then reused. RAG retrieves context. RAG is evaluated.
""",
                bib=None,
            )
            result = check_manuscript(main)
            codes = self.codes(result)
            self.assertIn("acronym-before-definition", codes)
            self.assertIn("acronym-case-drift", codes)
            self.assertIn("undefined-acronym", codes)

    def test_known_acronym_override_suppresses_heuristic(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "RAG retrieves context. RAG is evaluated.\n",
                bib=None,
            )
            result = check_manuscript(main, known_acronyms=["RAG"])
            self.assertNotIn("undefined-acronym", self.codes(result))

    def test_missing_include_is_p0(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(directory, "\\input{missing-section}\n", bib=None)
            result = check_manuscript(main)
            self.assertIn("missing-include", self.codes(result))
            self.assertFalse(result.ok)

    def test_missing_bibliography_source_does_not_guess_hallucination(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(directory, "\\cite{external-key}\n", bib=None)
            result = check_manuscript(main)
            self.assertIn("bibliography-source-missing", self.codes(result))
            self.assertNotIn("undefined-citation", self.codes(result))
            self.assertTrue(result.ok)

    def test_cli_json_output_and_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            main = self.write_project(
                directory,
                "\\ref{missing}\n",
                bib=None,
            )
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(main), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(1, completed.returncode)
            self.assertFalse(payload["ok"])
            self.assertEqual(1, payload["counts"]["P0"])


if __name__ == "__main__":
    unittest.main()
