# Anti AI-Defensive Writing Skill

[English](README.md) · **简体中文快速上手**

这是一个面向学术写作的英文 Skill，用来清理 AI 自动加入的防御性表达、
伪严谨分析、抽象难懂的句子和无意义格式，同时保护论文中的真实证据。
它还提供可选的论文完整性审计，用来检查 LaTeX 引用、图表顺序、BibTeX、
缩写定义和全文术语一致性。

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

清理一段文字：

```text
Use $anti-ai-defensive-writing to clean this results paragraph. Preserve every
number and citation, and do not add analyses or weaken supported claims.
```

只做审查、不全文改写：

```text
Use $anti-ai-defensive-writing in Audit mode. Report only consequential P0, P1,
and P2 problems and propose the smallest repair.
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

可直接复用的英文入口：

- [普通清理](prompts/quick-prompt.txt)
- [仅审查](prompts/audit-prompt.txt)
- [全文清理](prompts/full-manuscript-prompt.txt)
- [论文完整性审计](prompts/integrity-prompt.txt)

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

## 问题分级

- **P0，证据完整性：** 数字、引用、公式、指标、实验、条件或结论范围被修改或虚构，
  或者存在未解析引用与冲突 key。
- **P1，分析或结构问题：** 机械免责声明、无来源解释、结论瘫软、审稿人口吻、
  空洞抽象、结构歧义或术语歧义。
- **P2，非阻塞清理：** 无意义的破折号、斜体、粗体、括号、表格装饰或未使用记录。

P0 永远优先于风格。为了让句子更顺而损坏证据，属于失败的修改。

## 更多信息

完整设计、校验器和贡献方法请以英文 [README](README.md) 为准。本文件只提供
中文快速上手，避免维护两套可能不同步的完整规范。

项目采用 MIT License。
