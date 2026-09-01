# Anti AI-Defensive Writing Skill

[English](README.md) · **简体中文快速上手**

这是一个面向学术写作的英文 Skill，用来清理 AI 自动加入的防御性表达、
伪严谨分析、抽象难懂的句子和无意义格式，同时保护论文中的真实证据。
它还提供可选的论文完整性审计，用来检查 LaTeX 引用、图表顺序、BibTeX、
缩写定义和全文术语一致性；可以审计 review package 的匿名风险和 camera-ready
的身份恢复；并提供基于论文证据撰写 rebuttal 和 reviewer response 的独立工作流。

> 保留证据，删除虚构的严谨，写出证据能够支持的最强结论。

它不会机械删除所有限定词。已有来源的置信区间、定义清楚的 margin 或 probe、
必要的样本范围和真实 limitation 都应保留。没有来源的指标、统计检验、实验和
解释不能因为出现在 AI 草稿里就被当作事实。

## 一键安装

安装到 Codex 的个人 Skill 目录：

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex
```

先查看安装位置，不写入文件：

```bash
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent codex --dry-run
```

也可以安装到其他位置：

```bash
# Claude Code
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent claude

# 当前项目的 ./skills 目录
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --agent project

# 自定义 Skill 父目录
npx --yes github:ZF-Utokyo/anti-ai-defensive-writing --dir ./.agents/skills
```

安装器默认拒绝覆盖已有 Skill。显式使用 `--force` 时，它会先把旧版本移动到
带时间戳的备份目录，再安装新版本。

也可以继续手动复制：

```bash
cp -r skills/anti-ai-defensive-writing ~/.codex/skills/
```

## 使用方式

可以直接粘贴文字、附加论文文件，或者告诉 Codex 工作区中的文件路径。

清理一段文字：

```text
Use $anti-ai-defensive-writing to clean this results paragraph. Preserve every
number and citation, and do not add analyses or weaken supported claims.
```

只做审查、不全文改写：

```text
Use $anti-ai-defensive-writing in Audit mode. Report only consequential P0, P1,
and P2 problems and propose the smallest repair. Do not modify my files.
```

清理完整论文：

```text
Use $anti-ai-defensive-writing to clean this complete manuscript. Build an internal
claim-to-evidence ledger, remove duplicated defensive caveats, and run a global
integrity pass.
```

只做论文完整性审计：

```text
Use $anti-ai-defensive-writing to audit manuscript integrity. Check figure and
table citations, LaTeX references, BibTeX records, acronym definitions, and
terminology consistency without rewriting the prose.
```

如果希望同时在线核验文献：

```text
Use $anti-ai-defensive-writing in Integrity mode. Audit main.tex and run the
bundled checker with online reference verification. Do not modify my files.
```

撰写 rebuttal：

```text
Use $anti-ai-defensive-writing to draft a rebuttal from the supplied review and
manuscript. Answer each concern with existing evidence and an exact location.
Do not promise new work unless I have approved it.
```

检查双盲投稿包，包括附录和截图：

```text
Use $anti-ai-defensive-writing in Integrity mode to audit the exact upload package.
This is a double-blind review submission. Apply the supplied venue policy, run the
release checker, and visually inspect every PDF page, figure, and screenshot. Do
not modify my files or claim anonymity for anything you could not inspect.
```

可直接复用的英文入口：

- [普通清理](prompts/quick-prompt.txt)
- [仅审查](prompts/audit-prompt.txt)
- [全文清理](prompts/full-manuscript-prompt.txt)
- [论文完整性审计](prompts/integrity-prompt.txt)
- [Rebuttal 与 reviewer response](prompts/rebuttal-prompt.txt)
- [Review / publication package 审计](prompts/release-audit-prompt.txt)

## Skill 和 Checker 的区别

Skill 只有两条任务路径：

| 路径 | 用途 |
| --- | --- |
| Paper | 写作、清理或检查论文正文、证据、结构和参考文献 |
| Rebuttal | 把 reviewer comment 映射到现有证据、准确位置和作者批准的行动 |

Paper 内部只有两个 release profile：

| Release profile | 包含阶段 | 身份规则 |
| --- | --- | --- |
| Review package | Submission、revision、resubmission | 根据 venue 明确选择 `none`、`single-blind` 或 `double-blind` |
| Publication package | Accepted、camera-ready | 恢复经过确认的作者信息，清理 review 阶段占位符 |

“Submission”本身不代表匿名。Rebuttal 单独处理，因为它的主要产物是对 reviewer
comment 的回复，而不是论文正文。

这个项目还为 Paper 路径提供三个确定性安全网：

| 组件 | 适合解决的问题 | 使用方式 |
| --- | --- | --- |
| Skill | 写作、清理、审查，以及判断限定语或术语是否必要 | 在对话中调用 `$anti-ai-defensive-writing` |
| 修改对比 Checker | 检查 AI 修改前后是否丢失或发明证据 | 对 `before` 和 `after` 文件运行脚本 |
| 论文完整性 Checker | 检查完整 LaTeX 项目的结构与文献 | 对 `main.tex` 运行脚本 |
| Release Checker | 检查实际上传包中的身份泄露与打包残留 | 对上传目录运行 `check_release_package.py` |

Checker 不判断文章“像不像 AI”。脚本负责数字、引用、公式、label、BibTeX 和
release package 表面等确定性问题；Skill 负责判断免责声明是否多余、claim 是否
被削弱、术语是否真的等价等语义问题。普通用户只需要安装 Skill 并告诉 Codex
目标，Codex 会在需要时运行 Checker。

`npx` 命令只负责安装 Skill，不提供单独的 `check` 子命令。下面的脚本命令
默认从克隆后的仓库根目录运行。通过 `npx` 安装到 Codex 后，脚本位于：

```text
~/.codex/skills/anti-ai-defensive-writing/scripts/
```

Claude 的对应目录是 `~/.claude/skills/anti-ai-defensive-writing/scripts/`；
项目安装的对应目录是 `./skills/anti-ai-defensive-writing/scripts/`。

## 修改前后证据检查

如果有 AI 修改前后的两个文本或 Markdown 文件，运行：

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_academic_rewrite.py \
  before.md after.md
```

它会检查数字、LaTeX 和数字引用、公式、URL、代码块、Markdown 标题层级，
以及只在修改后出现的分析术语和审稿人口吻。它不是 AI 文本检测器，而是检查
修改有没有损坏或发明证据。

## 论文完整性审计

对 LaTeX 项目运行本地只读检查：

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_manuscript_integrity.py \
  main.tex
```

它会检查未解析或重复的 label/citation key、没有正文引用或引用顺序异常的
Figure/Table、常见 BibTeX 字段与 DOI/URL 问题，以及缩写首次定义和大小写。
默认命令不联网，也不会自动修改论文。

如果需要本地检查加在线文献核验，一条命令即可完成：

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_manuscript_integrity.py \
  main.tex --verify-online
```

脚本会先查
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)；
如果没有得到标题完全匹配的结果，再自动回退到
[DBLP 文献检索 API](https://dblp.org/faq/How%2Bto%2Buse%2Bthe%2Bdblp%2Bsearch%2BAPI.html)。
不需要 API key，也不需要安装额外 Python 包。默认只核验正文实际引用的 BibTeX
条目；`--verify-all-bib` 可以检查整个文献库，`--online-provider` 可以指定
数据源，`--mailto` 可以提供 Crossref 建议的联系邮箱。

只有显式加入 `--verify-online` 时才会联网，并且只发送检索所需的题目、
第一作者、年份和 DOI，不上传论文正文，不会自动修改论文或 `.bib`。结果会
区分 verified、likely_match、ambiguous、not_found、conflicting_metadata、
provider_error 和 unverifiable，并尽量给出字段差异与来源链接。

[Citesurely](https://citesurely.com/) 和
[CiteScanning](https://www.modelscope.cn/studios/aivolcano/CiteScanning/summary)
可以继续作为人工二次核对工具，但一键流程不依赖它们的网页界面或未公开接口。
查不到不能直接判定为 AI 虚构；查到元数据也不能证明该论文支持正文中的具体
claim。只有用户明确要求时才审查 citation 是否支持 claim；不能因为当前只
提供了摘要或引言，就判断完整论文缺少证据。

## Review package 与 camera-ready 检查

对实际准备上传的目录运行 Checker，而不是只检查 `main.tex`。双盲投稿示例：

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  submission/ --release review --anonymity double-blind \
  --identity-term "Author Name" \
  --identity-term "github.com/author-account"
```

单盲和不匿名审稿分别使用 `--anonymity single-blind` 与 `--anonymity none`。
Camera-ready 使用：

```bash
python3 skills/anti-ai-defensive-writing/scripts/check_release_package.py \
  camera-ready/ --release publication
```

脚本会只读扫描文件名、目录名、可读源码、常见 LaTeX 作者字段、email、ORCID、
本机用户路径、仓库 URL、可读取的 PDF author metadata、匿名占位符和打包残留。
`--identity-term` 可以重复填写已知作者名、用户名、单位、域名、项目名和路径片段。

截图、PDF 页面、slide 和视频会单独列为 `manual_checks`。Skill 应继续做视觉
检查，寻找姓名、用户名、头像、浏览器标签、账号菜单、终端路径、水印，以及
参与者或标注者身份。脚本本身不做 OCR，也不理解具体 venue policy；纯文本扫描
没有发现问题不等于“已经证明匿名”。无法检查的附件、metadata、链接或视觉内容
必须标记为 unresolved。

## 如何看检查结果

- **P0，证据或发布完整性：** 数字、引用、公式、指标、实验、条件或结论范围被修改
  或虚构，存在未解析引用与冲突 key，或者身份信息违反已提供的发布政策。
- **P1，分析或结构问题：** 机械免责声明、无来源解释、结论瘫软、审稿人口吻、
  空洞抽象、结构歧义、术语歧义，或者需要依据 venue policy 确认的身份表面。
- **P2，非阻塞清理：** 无意义的破折号、斜体、粗体、括号、表格装饰、未使用记录
  或打包残留。

P0 永远优先于风格。为了让句子更顺而损坏证据，属于失败的修改。

在线文献核验还会返回：

- `verified`：关键字段一致；
- `likely_match`：基本匹配，但字段不完整或 venue 可能使用别名；
- `ambiguous` 或 `not_found`：自动核验无法确定，不能据此判定文献是虚构的；
- `conflicting_metadata`：作者、标题、年份或 DOI 等重要字段冲突；
- `provider_error` 或 `unverifiable`：服务失败，或者记录缺少足够的检索字段。

默认情况下，P0 会让脚本返回失败状态；加入 `--strict` 后，P1 和 P2 也会返回
失败状态。脚本只报告问题，不会自动修改论文或参考文献。

Review package 必须显式提供 `--anonymity`，避免工具把所有 submission 自动
当作双盲投稿。Camera-ready 恢复作者身份后，参与者、标注者和工作人员隐私仍然
需要检查，不能跟着作者信息一起自动公开。

## 更多信息

完整设计、校验器和贡献方法请以英文 [README](README.md) 为准。本文件只提供
中文快速上手，避免维护两套可能不同步的完整规范。

项目采用 MIT License。
