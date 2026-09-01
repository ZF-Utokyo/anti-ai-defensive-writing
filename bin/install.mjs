#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SKILL_NAME = "anti-ai-defensive-writing";
const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(scriptDirectory, "..");
const sourceDirectory = path.join(packageRoot, "skills", SKILL_NAME);
const packageMetadata = JSON.parse(
  fs.readFileSync(path.join(packageRoot, "package.json"), "utf8")
);

function printHelp() {
  console.log(`
Anti AI-Defensive Writing installer

Usage:
  anti-ai-defensive-writing [options]

Options:
  --agent <name>  Install for codex, claude, or project (default: codex)
  --dir <path>    Override the parent Skill directory
  --dry-run       Show the resolved installation plan without writing files
  --force         Replace an existing installation after creating a backup
  --help, -h      Show this help
  --version, -v   Show the package version

Examples:
  anti-ai-defensive-writing --dry-run
  anti-ai-defensive-writing --agent codex
  anti-ai-defensive-writing --agent project
  anti-ai-defensive-writing --dir ./.agents/skills
`);
}

function defaultParent(agent) {
  if (agent === "codex") {
    return path.join(os.homedir(), ".codex", "skills");
  }
  if (agent === "claude") {
    return path.join(os.homedir(), ".claude", "skills");
  }
  if (agent === "project") {
    return path.resolve(process.cwd(), "skills");
  }
  throw new Error(`Unknown agent: ${agent}. Use codex, claude, or project.`);
}

function parseArguments(argv) {
  let agent = "codex";
  let parentOverride;
  let dryRun = false;
  let force = false;

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--help" || argument === "-h") {
      printHelp();
      return { exit: true };
    }
    if (argument === "--version" || argument === "-v") {
      console.log(packageMetadata.version);
      return { exit: true };
    }
    if (argument === "--dry-run") {
      dryRun = true;
      continue;
    }
    if (argument === "--force") {
      force = true;
      continue;
    }
    if (argument === "--agent" || argument === "--dir") {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) {
        throw new Error(`${argument} requires a value.`);
      }
      if (argument === "--agent") {
        agent = value;
      } else {
        parentOverride = path.resolve(process.cwd(), value);
      }
      index += 1;
      continue;
    }
    throw new Error(`Unknown option: ${argument}`);
  }

  const parentDirectory = parentOverride ?? defaultParent(agent);
  const targetDirectory = path.join(parentDirectory, SKILL_NAME);
  const relativeTarget = path.relative(parentDirectory, targetDirectory);
  if (relativeTarget !== SKILL_NAME) {
    throw new Error("Refusing to install outside the resolved Skill directory.");
  }

  return { agent, dryRun, force, parentDirectory, targetDirectory };
}

function verifySkill(directory) {
  const required = ["SKILL.md", path.join("agents", "openai.yaml")];
  for (const relativePath of required) {
    if (!fs.statSync(path.join(directory, relativePath), { throwIfNoEntry: false })?.isFile()) {
      throw new Error(`Incomplete Skill package: missing ${relativePath}.`);
    }
  }
}

function backupPathFor(targetDirectory) {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "");
  let candidate = `${targetDirectory}.backup-${stamp}`;
  let suffix = 1;
  while (fs.existsSync(candidate)) {
    candidate = `${targetDirectory}.backup-${stamp}-${suffix}`;
    suffix += 1;
  }
  return candidate;
}

function install(options) {
  verifySkill(sourceDirectory);
  const existing = fs.lstatSync(options.targetDirectory, { throwIfNoEntry: false });
  if (existing?.isSymbolicLink()) {
    throw new Error(`Refusing to replace symbolic link: ${options.targetDirectory}`);
  }
  if (existing && !options.force && !options.dryRun) {
    throw new Error(
      `Skill already exists: ${options.targetDirectory}\n` +
      "Run with --dry-run to inspect the target or --force to create a backup and replace it."
    );
  }

  console.log(`Agent: ${options.agent}`);
  console.log(`Source: ${sourceDirectory}`);
  console.log(`Target: ${options.targetDirectory}`);
  if (existing && options.force) {
    console.log("Existing target: will be moved to a timestamped backup");
  } else if (existing) {
    console.log("Existing target: installation would stop unless --force is supplied");
  }
  if (options.dryRun) {
    console.log("Dry run complete. No files were changed.");
    return;
  }

  fs.mkdirSync(options.parentDirectory, { recursive: true });
  const stagingDirectory = path.join(
    options.parentDirectory,
    `.${SKILL_NAME}.install-${process.pid}-${Date.now()}`
  );
  let backupDirectory;

  try {
    fs.cpSync(sourceDirectory, stagingDirectory, {
      recursive: true,
      errorOnExist: true,
      force: false
    });
    verifySkill(stagingDirectory);

    if (existing) {
      backupDirectory = backupPathFor(options.targetDirectory);
      fs.renameSync(options.targetDirectory, backupDirectory);
    }
    fs.renameSync(stagingDirectory, options.targetDirectory);
  } catch (error) {
    if (fs.existsSync(stagingDirectory)) {
      fs.rmSync(stagingDirectory, { recursive: true, force: true });
    }
    if (backupDirectory && !fs.existsSync(options.targetDirectory)) {
      fs.renameSync(backupDirectory, options.targetDirectory);
    }
    throw error;
  }

  console.log(`Installed ${SKILL_NAME}.`);
  if (backupDirectory) {
    console.log(`Previous installation backed up to: ${backupDirectory}`);
  }
}

function main() {
  try {
    const options = parseArguments(process.argv.slice(2));
    if (!options.exit) {
      install(options);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exitCode = 1;
  }
}

main();
