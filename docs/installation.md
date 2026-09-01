# Installation and updates

## Install for Codex

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex
```

This installs the Skill at:

```text
~/.codex/skills/anti-ai-defensive-writing/
```

The `npx` command installs the Skill. It does not expose a separate `check`
subcommand; an agent can run the bundled Python checkers, or you can run them
directly from a cloned repository.

## Preview without writing

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing \
  --agent codex --dry-run
```

The dry run prints the source and resolved destination without creating or
replacing files.

## Other destinations

Install for Claude Code:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent claude
```

Install in the current project's `./skills` directory:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent project
```

Choose a custom parent directory:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing \
  --dir ./.agents/skills
```

Default installed locations are:

| Agent | Skill directory | Checker directory |
| --- | --- | --- |
| Codex | `~/.codex/skills/anti-ai-defensive-writing/` | `~/.codex/skills/anti-ai-defensive-writing/scripts/` |
| Claude Code | `~/.claude/skills/anti-ai-defensive-writing/` | `~/.claude/skills/anti-ai-defensive-writing/scripts/` |
| Project | `./skills/anti-ai-defensive-writing/` | `./skills/anti-ai-defensive-writing/scripts/` |

## Replace an existing installation

The installer refuses to overwrite an existing Skill by default. To update it,
run the same installation command with `--force`:

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing \
  --agent codex --force
```

Before replacement, the installer moves the old directory to a timestamped backup
next to the installation. It refuses to replace a symbolic-link target.

Use `--dry-run` first when you want to verify the destination.

## Installer options

| Option | Meaning |
| --- | --- |
| `--agent codex|claude|project` | Select a standard destination; defaults to `codex` |
| `--dir PATH` | Override the parent Skill directory |
| `--dry-run` | Print the installation plan without writing |
| `--force` | Back up and replace an existing installation |
| `--version`, `-v` | Print the package version |
| `--help`, `-h` | Print installer help |

## Manual installation

Clone the repository and copy the Skill directory into the agent's Skill folder.
For Codex:

```bash
cp -r skills/anti-ai-defensive-writing ~/.codex/skills/
```

The installed directory must contain `SKILL.md`, `agents/openai.yaml`, the
`references/` directory, and the `scripts/` directory.
