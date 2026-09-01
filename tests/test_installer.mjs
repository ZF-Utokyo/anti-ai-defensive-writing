import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = path.join(repositoryRoot, "bin", "install.mjs");
const skillName = "anti-ai-defensive-writing";

function temporaryDirectory(t) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "anti-ai-writing-test-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  return directory;
}

function runInstaller(arguments_, cwd = repositoryRoot) {
  return spawnSync(process.execPath, [installer, ...arguments_], {
    cwd,
    encoding: "utf8"
  });
}

test("dry run resolves the target without writing files", (t) => {
  const parent = temporaryDirectory(t);
  const result = runInstaller(["--dir", parent, "--dry-run"]);

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /No files were changed/);
  assert.equal(fs.existsSync(path.join(parent, skillName)), false);
});

test("custom directory install copies only the Skill package", (t) => {
  const parent = temporaryDirectory(t);
  const result = runInstaller(["--dir", parent]);
  const target = path.join(parent, skillName);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.existsSync(path.join(target, "SKILL.md")), true);
  assert.equal(fs.existsSync(path.join(target, "agents", "openai.yaml")), true);
  assert.equal(
    fs.existsSync(path.join(target, "scripts", "check_manuscript_integrity.py")),
    true
  );
  assert.equal(
    fs.existsSync(path.join(target, "scripts", "verify_bibliography_online.py")),
    true
  );
  assert.equal(
    fs.existsSync(path.join(target, "references", "manuscript-integrity.md")),
    true
  );
  assert.equal(
    fs.existsSync(path.join(target, "references", "rebuttal-workflow.md")),
    true
  );
  assert.equal(fs.existsSync(path.join(target, "README.md")), false);
});

test("existing installation is refused by default", (t) => {
  const parent = temporaryDirectory(t);
  assert.equal(runInstaller(["--dir", parent]).status, 0);

  const result = runInstaller(["--dir", parent]);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Skill already exists/);
});

test("dry run can inspect an existing installation without replacing it", (t) => {
  const parent = temporaryDirectory(t);
  const target = path.join(parent, skillName);
  assert.equal(runInstaller(["--dir", parent]).status, 0);
  fs.writeFileSync(path.join(target, "local-note.txt"), "unchanged", "utf8");

  const result = runInstaller(["--dir", parent, "--dry-run"]);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /installation would stop unless --force/);
  assert.equal(fs.readFileSync(path.join(target, "local-note.txt"), "utf8"), "unchanged");
});

test("force replacement creates a recoverable backup", (t) => {
  const parent = temporaryDirectory(t);
  const target = path.join(parent, skillName);
  assert.equal(runInstaller(["--dir", parent]).status, 0);
  fs.writeFileSync(path.join(target, "local-note.txt"), "preserve me", "utf8");

  const result = runInstaller(["--dir", parent, "--force"]);
  const backups = fs
    .readdirSync(parent)
    .filter((name) => name.startsWith(`${skillName}.backup-`));

  assert.equal(result.status, 0, result.stderr);
  assert.equal(backups.length, 1);
  assert.equal(
    fs.readFileSync(path.join(parent, backups[0], "local-note.txt"), "utf8"),
    "preserve me"
  );
  assert.equal(fs.existsSync(path.join(target, "local-note.txt")), false);
});

test("symbolic-link targets are never replaced", (t) => {
  const parent = temporaryDirectory(t);
  const realDirectory = path.join(parent, "real-skill");
  const target = path.join(parent, skillName);
  fs.mkdirSync(realDirectory);
  fs.symlinkSync(realDirectory, target, "dir");

  const result = runInstaller(["--dir", parent, "--force"]);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Refusing to replace symbolic link/);
  assert.equal(fs.lstatSync(target).isSymbolicLink(), true);
});

test("unknown agent fails without creating a target", (t) => {
  const cwd = temporaryDirectory(t);
  const result = runInstaller(["--agent", "unknown"], cwd);

  assert.equal(result.status, 1);
  assert.match(result.stderr, /Unknown agent/);
  assert.equal(fs.existsSync(path.join(cwd, "skills", skillName)), false);
});
