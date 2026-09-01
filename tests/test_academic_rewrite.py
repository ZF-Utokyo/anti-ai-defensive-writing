import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "anti-ai-defensive-writing" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_academic_rewrite import check_rewrite  # noqa: E402


class AcademicRewriteChecks(unittest.TestCase):
    def codes(self, findings):
        return [item.code for item in findings]

    def test_clean_rewrite_preserves_evidence(self):
        before = "While promising, accuracy is 75.4% on Dataset A versus 72.1%."
        after = "Accuracy is 75.4% on Dataset A versus 72.1%."
        result = check_rewrite(before, after)
        self.assertTrue(result.ok)
        self.assertEqual([], result.warnings)

    def test_numeric_drift_is_p0(self):
        result = check_rewrite("Accuracy is 75.4%.", "Accuracy is 76.4%.")
        self.assertIn("numeric-drift", self.codes(result.errors))
        self.assertEqual("P0", result.errors[0].severity)

    def test_introduced_confidence_interval_is_p0(self):
        result = check_rewrite("Accuracy is 81.2.", "Accuracy is 81.2 (95% CI, 80.6 to 81.8).")
        self.assertIn("introduced-analysis", self.codes(result.errors))
        self.assertIn("numeric-drift", self.codes(result.errors))

    def test_quarantined_draft_numbers_require_explicit_allowance(self):
        before = "An unsourced Robustness Index of 0.91 and confidence margin of 1.7 were added."
        after = "The unsourced metrics were removed."
        locked = check_rewrite(before, after)
        allowed = check_rewrite(before, after, allow_drop_numbers=["0.91", "1.7"])
        self.assertIn("numeric-drift", self.codes(locked.errors))
        self.assertTrue(allowed.ok)

    def test_invalid_number_allowance_fails_closed(self):
        result = check_rewrite(
            "Accuracy is 81.2.",
            "Accuracy is 81.2.",
            allow_drop_numbers=["0.91"],
        )
        self.assertIn("invalid-number-allowance", self.codes(result.errors))

    def test_supplied_confidence_interval_is_preserved(self):
        text = "The effect is 2.4 points (95% CI, 1.1 to 3.7)."
        result = check_rewrite(text, text)
        self.assertTrue(result.ok)

    def test_numeric_format_normalizes_sign_and_percent_spacing(self):
        before = "The change is −2.0% on Dataset A."
        after = "On Dataset A, the change is -2.0 %."
        result = check_rewrite(before, after)
        self.assertTrue(result.ok)

    def test_style_cleanup_can_preserve_citation_and_values(self):
        before = "# Results\n\nAccuracy is 84.6%—up from 81.3% [7]."
        after = "# Results\n\nAccuracy is 84.6%, up from 81.3% [7]."
        result = check_rewrite(before, after)
        self.assertTrue(result.ok)

    def test_references_math_urls_and_code_are_protected(self):
        before = (
            "See \\cite{smith2024} and Eq. \\eqref{eq:loss}. "
            "The objective is $L=x^2$. https://example.org/paper\n\n"
            "```python\nscore = 3\n```"
        )
        after = "See the paper. The objective is changed."
        result = check_rewrite(before, after)
        codes = self.codes(result.errors)
        self.assertIn("latex-reference-drift", codes)
        self.assertIn("url-drift", codes)
        self.assertIn("math-drift", codes)
        self.assertIn("code-block-drift", codes)

    def test_new_defensive_voice_is_warning(self):
        result = check_rewrite(
            "Accuracy improves on Dataset A.",
            "Accuracy may suggest an improvement on Dataset A, but we cannot claim a gain.",
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            ["introduced-defensiveness", "introduced-defensiveness"],
            self.codes(result.warnings),
        )

    def test_explicit_analysis_override(self):
        result = check_rewrite(
            "Accuracy is 81.2.",
            "Accuracy is 81.2 with a confidence interval.",
            allow_new_analysis=True,
        )
        self.assertTrue(result.ok)

    def test_heading_structure_can_be_locked_or_allowed(self):
        before = "# Result\n\n## Main comparison\n"
        after = "# Result\n\n### Main comparison\n"
        locked = check_rewrite(before, after)
        allowed = check_rewrite(before, after, allow_structure_change=True)
        self.assertIn("heading-structure-drift", self.codes(locked.errors))
        self.assertTrue(allowed.ok)


if __name__ == "__main__":
    unittest.main()
