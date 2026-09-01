import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "anti-ai-defensive-writing" / "scripts"
SCRIPT = SCRIPT_DIR / "check_release_package.py"
sys.path.insert(0, str(SCRIPT_DIR))

from check_release_package import check_release_package  # noqa: E402


class ReleasePackageChecks(unittest.TestCase):
    def codes(self, result):
        return [item.code for item in result.findings]

    def test_double_blind_review_finds_identity_surfaces(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath("main.tex").write_text(
                r"""
\author{Jane Example}
\affiliation{Example University}
Contact jane@example.edu or see https://github.com/jane/example.
The log was saved under /Users/jane/project/output.txt.
\section*{Acknowledgements}
Supported by grant 123.
""",
                encoding="utf-8",
            )
            root.joinpath("Jane-Example-notes.txt").write_text(
                "internal release note", encoding="utf-8"
            )
            result = check_release_package(
                root,
                release="review",
                anonymity="double-blind",
                identity_terms=["Jane Example"],
            )
            codes = self.codes(result)
            self.assertIn("nonanonymous-author-field", codes)
            self.assertIn("possible-email-identity", codes)
            self.assertIn("local-user-path", codes)
            self.assertIn("review-repository-url", codes)
            self.assertIn("review-acknowledgement-or-funding", codes)
            self.assertIn("identity-term-in-path", codes)
            self.assertFalse(result.ok)

    def test_single_blind_does_not_apply_double_blind_removal(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / "main.tex"
            main.write_text(
                "\\author{Jane Example}\nContact jane@example.edu.\n",
                encoding="utf-8",
            )
            result = check_release_package(
                Path(directory),
                release="review",
                anonymity="single-blind",
                identity_terms=["Jane Example"],
            )
            self.assertNotIn("nonanonymous-author-field", self.codes(result))
            self.assertNotIn("possible-email-identity", self.codes(result))
            self.assertTrue(result.ok)

    def test_bibliography_identity_match_is_policy_dependent(self):
        with tempfile.TemporaryDirectory() as directory:
            bibliography = Path(directory) / "refs.bib"
            bibliography.write_text(
                "@article{self, author={Jane Example}, title={Prior Work}}\n",
                encoding="utf-8",
            )
            result = check_release_package(
                Path(directory),
                release="review",
                anonymity="double-blind",
                identity_terms=["Jane Example"],
            )
            finding = next(
                item
                for item in result.findings
                if item.code == "identity-term-in-bibliography"
            )
            self.assertEqual("P1", finding.severity)
            self.assertTrue(result.ok)

    def test_publication_finds_review_placeholder(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / "main.tex"
            main.write_text(
                "\\author{Anonymous Authors}\nRepository omitted for blind review.\n"
                "https://anonymous.4open.science/r/example\n",
                encoding="utf-8",
            )
            result = check_release_package(
                Path(directory),
                release="publication",
            )
            self.assertIn("review-placeholder-in-publication", self.codes(result))
            self.assertIn("anonymous-url-in-publication", self.codes(result))
            self.assertNotIn("possible-email-identity", self.codes(result))

    def test_pdf_author_metadata_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.4\n1 0 obj << /Author (Jane Example) >>\n%%EOF")
            result = check_release_package(
                Path(directory),
                release="review",
                anonymity="double-blind",
            )
            self.assertIn("pdf-author-metadata", self.codes(result))
            self.assertFalse(result.ok)

    def test_visual_artifacts_are_never_silently_certified(self):
        with tempfile.TemporaryDirectory() as directory:
            screenshot = Path(directory) / "appendix-annotator-screenshot.png"
            screenshot.write_bytes(b"not a real image")
            result = check_release_package(
                Path(directory),
                release="review",
                anonymity="double-blind",
            )
            paths = [item.path for item in result.manual_checks]
            self.assertIn(str(screenshot.resolve()), paths)
            self.assertIn(
                "visual-identity-review",
                [item.code for item in result.manual_checks],
            )

    def test_readable_svg_is_scanned_and_still_requires_visual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "appendix-screenshot.svg"
            image.write_text(
                '<svg><text>Mei Chen mchen@example.edu '
                "/Users/mei/output.csv</text></svg>",
                encoding="utf-8",
            )
            result = check_release_package(
                Path(directory),
                release="review",
                anonymity="double-blind",
                identity_terms=["Mei Chen"],
            )
            codes = self.codes(result)
            self.assertIn("identity-term-in-text", codes)
            self.assertIn("possible-email-identity", codes)
            self.assertIn("local-user-path", codes)
            self.assertIn(
                "visual-identity-review",
                [item.code for item in result.manual_checks],
            )

    def test_review_cli_requires_anonymity_and_returns_configuration_error(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    directory,
                    "--release",
                    "review",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("require --anonymity", completed.stderr)

    def test_cli_json_separates_findings_and_manual_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "figure.png").write_bytes(b"image")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    directory,
                    "--release",
                    "publication",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(0, completed.returncode)
            self.assertEqual("publication", payload["release"])
            self.assertIn("findings", payload)
            self.assertIn("manual_checks", payload)


if __name__ == "__main__":
    unittest.main()
