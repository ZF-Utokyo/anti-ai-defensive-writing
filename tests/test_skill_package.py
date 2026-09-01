from pathlib import Path
import json
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

    def test_whole_manuscript_reference_is_routed_from_skill(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("references/whole-manuscript-workflow.md", text)
        workflow = SKILL_DIR.joinpath(
            "references", "whole-manuscript-workflow.md"
        ).read_text(encoding="utf-8")
        self.assertIn("evidence ledger", workflow.lower())
        self.assertIn("Do not add a paper-level defensiveness score", workflow)

    def test_manuscript_integrity_reference_is_routed_from_skill(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("references/manuscript-integrity.md", text)
        workflow = SKILL_DIR.joinpath(
            "references", "manuscript-integrity.md"
        ).read_text(encoding="utf-8")
        self.assertIn("first meaningful in-text citation", workflow)
        self.assertIn("A missing result is not proof", workflow)
        self.assertIn("terminology ledger", workflow.lower())
        self.assertIn("Do not start a claim-support audit unless", workflow)
        self.assertIn("--verify-online", workflow)
        self.assertIn("Crossref", workflow)

    def test_rebuttal_reference_is_routed_from_skill(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("references/rebuttal-workflow.md", text)
        workflow = SKILL_DIR.joinpath(
            "references", "rebuttal-workflow.md"
        ).read_text(encoding="utf-8")
        self.assertIn("comment-to-evidence ledger", workflow)
        self.assertIn("Authorized action", workflow)
        self.assertIn("never write \"we added,\"", workflow)
        self.assertRegex(workflow, r"Do not predict score\s+changes")

    def test_release_package_reference_is_routed_from_skill(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("references/release-package.md", text)
        self.assertIn("review package", text)
        self.assertIn("publication package", text)
        workflow = SKILL_DIR.joinpath(
            "references", "release-package.md"
        ).read_text(encoding="utf-8")
        self.assertIn("none`, `single-blind`, or `double-blind", workflow)
        self.assertIn("Never claim that a text-only scan proves anonymity", workflow)
        self.assertIn("participant,\ninterviewee, annotator", workflow)

    def test_repository_prompt_entry_points_exist(self):
        prompt_names = {
            "quick-prompt.txt",
            "audit-prompt.txt",
            "full-manuscript-prompt.txt",
            "integrity-prompt.txt",
            "rebuttal-prompt.txt",
            "release-audit-prompt.txt",
        }
        prompt_directory = ROOT / "prompts"
        self.assertEqual(
            prompt_names,
            {path.name for path in prompt_directory.glob("*.txt")},
        )

    def test_npm_manifest_installs_the_skill(self):
        manifest = json.loads(ROOT.joinpath("package.json").read_text(encoding="utf-8"))
        self.assertEqual("anti-ai-defensive-writing", manifest["name"])
        self.assertEqual("0.5.0", manifest["version"])
        self.assertEqual("bin/install.mjs", manifest["bin"]["anti-ai-defensive-writing"])
        self.assertIn("skills/anti-ai-defensive-writing", manifest["files"])
        self.assertIn("prompts", manifest["files"])
        self.assertIn("docs", manifest["files"])
        self.assertIn("assets", manifest["files"])
        self.assertNotIn("dependencies", manifest)

    def test_integrity_checker_is_packaged(self):
        checker = SKILL_DIR / "scripts" / "check_manuscript_integrity.py"
        verifier = SKILL_DIR / "scripts" / "verify_bibliography_online.py"
        self.assertTrue(checker.is_file())
        self.assertTrue(verifier.is_file())
        source = checker.read_text(encoding="utf-8")
        self.assertIn("check_manuscript", source)
        verifier_source = verifier.read_text(encoding="utf-8")
        for candidate in (source, verifier_source):
            self.assertNotRegex(
                candidate,
                r"(?m)^(?:from|import) (?:requests|httpx|aiohttp)",
            )

    def test_readme_documents_one_command_online_verification(self):
        for readme in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
            text = readme.read_text(encoding="utf-8")
            self.assertIn("--verify-online", text)
            self.assertIn("Crossref", text)

    def test_repository_readme_links_exist(self):
        documents = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            *ROOT.joinpath("docs").glob("*.md"),
        ]
        for document in documents:
            text = document.read_text(encoding="utf-8")
            targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
            targets.extend(re.findall(r'(?:href|src)="([^"]+)"', text))
            missing = []
            for target in targets:
                if target.startswith(("http://", "https://", "#")):
                    continue
                local_target = target.split("#", 1)[0]
                if local_target and not document.parent.joinpath(local_target).exists():
                    missing.append(target)
            self.assertEqual([], missing, msg=str(document))


if __name__ == "__main__":
    unittest.main()
