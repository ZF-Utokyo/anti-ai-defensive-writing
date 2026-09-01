from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "anti-ai-defensive-writing"
SKILL_FILE = SKILL_DIR / "SKILL.md"


class SkillPackageChecks(unittest.TestCase):
    def test_frontmatter_and_directory_name_match(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(?P<body>.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match)
        frontmatter = match.group("body")
        self.assertRegex(frontmatter, r"(?m)^name: anti-ai-defensive-writing$")
        self.assertRegex(frontmatter, r"(?m)^description: >$")
        self.assertEqual("anti-ai-defensive-writing", SKILL_DIR.name)

    def test_referenced_markdown_files_exist(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        targets = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text)
        self.assertGreater(len(targets), 0)
        missing = [target for target in targets if not (SKILL_DIR / target).exists()]
        self.assertEqual([], missing)

    def test_package_contains_no_scaffold_markers(self):
        files = [SKILL_FILE, *SKILL_DIR.joinpath("references").glob("*.md")]
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\b(?:TODO|TBD)\b", msg=str(path))

    def test_ui_prompt_invokes_the_skill(self):
        metadata = SKILL_DIR.joinpath("agents", "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$anti-ai-defensive-writing", metadata)


if __name__ == "__main__":
    unittest.main()
