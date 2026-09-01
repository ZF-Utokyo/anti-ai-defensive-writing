<p align="center">
  <img src="assets/readme-icon.svg" width="88" alt="划掉多余横线并保留证据的论文图标">
</p>

<h1 align="center">Anti AI-Defensive Writing Skill</h1>

<p align="center"><a href="README.md">English</a> · <strong>简体中文</strong></p>

<p align="center"><em>AI 写作是不是又加了 em dash、凭空出现的置信区间、
莫名其妙的指标，以及没完没了的 “we do not claim” 式免责声明？</em></p>

## 一键安装

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex
```

安装后可以粘贴文字、附加论文，或者让 Codex 读取工作区文件。普通用户不需要
自己运行 Checker。

## 三个可复制入口

### 清理论文

```text
Use $anti-ai-defensive-writing to clean this results section. Preserve every
number, citation, equation, and supported claim. Do not add analyses, metrics,
experiments, or reviewer-style caveats.
```

### 检查投稿包或 camera-ready

```text
Use $anti-ai-defensive-writing in Integrity mode to audit the exact upload package.
Apply the supplied venue policy, run the release checker, and visually inspect
every PDF page, figure, and screenshot. Do not modify my files or claim anonymity
for anything you could not inspect.
```

Review package 需要明确说明 `none`、`single-blind` 或 `double-blind`。
“Submission”本身不代表匿名。

### 撰写 rebuttal

```text
Use $anti-ai-defensive-writing to draft a rebuttal from the supplied review and
manuscript. Answer each concern with existing evidence and an exact location. Do
not promise new work unless I have approved it.
```

## 两条任务路径

| 路径 | 用途 |
| --- | --- |
| **Paper** | 写作、清理或检查论文正文、证据、结构、文献和发布包 |
| **Rebuttal** | 把 reviewer comment 映射到现有证据、准确位置和作者批准的行动 |

Paper 内部有两个 release profile：

| Release profile | 包含阶段 | 身份规则 |
| --- | --- | --- |
| **Review package** | Submission、revision、resubmission | 根据 venue 明确选择 `none`、`single-blind` 或 `double-blind` |
| **Publication package** | Accepted、camera-ready | 恢复经过确认的作者信息，清理 review 阶段占位符 |

Rebuttal 单独处理，因为它的主要产物是对 reviewer comment 的回复，而不是论文
正文。

## 修改前后

AI 防御性版本：

> While these findings are promising, they should be interpreted with caution, and
> we cannot claim that the method consistently improves performance.

已有证据：Dataset A 上的准确率从 72.1% 提升到 75.4%。

清理后：

> The method improves accuracy from 72.1% to 75.4% on Dataset A.

Dataset A 已经给出了真实边界，额外的免责声明没有增加证据。核心原则是：

> 保留证据，删除虚构的严谨，写出证据能够支持的最强结论。

## 三个 Checker

| Checker | 检查内容 | 直接命令 |
| --- | --- | --- |
| 修改对比 Checker | 数字、引用、公式、URL、结构和新增的虚构分析 | `check_academic_rewrite.py before after` |
| 论文完整性 Checker | LaTeX 引用、图表顺序、BibTeX、缩写和术语线索 | `check_manuscript_integrity.py main.tex`；加入 `--verify-online` 后使用 Crossref，并在需要时回退到 DBLP |
| Release Checker | Review 匿名、camera-ready 身份、metadata、路径和上传包残留 | `check_release_package.py PACKAGE --release ...` |

三个脚本都不依赖额外 Python 包，默认只读，也不判断文字“像不像 AI”。Skill
负责语义判断；Checker 保护确定性信息，并列出仍需视觉或 venue policy 确认的内容。

## 详细文档

- [安装位置、更新和备份](docs/installation.md)
- [Checker 命令、全部参数、严重级别和结果含义](docs/checkers.md)
- [Review 匿名与 camera-ready 发布审计](docs/release-audits.md)
- [可直接使用的 Prompt](prompts/)
- [Skill 完整规则](skills/anti-ai-defensive-writing/SKILL.md)
- [评测案例](evals/cases.md)

## 参与贡献

欢迎提交真实的误报案例和失败场景。请同时说明可观察的预期行为，具体方式见
[CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT
