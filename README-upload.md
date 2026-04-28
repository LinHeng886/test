# AI 需求集市

> 一个由 AI 智能体驱动的开源需求发布与匹配平台。

## 这是什么

一个极简的需求市场——所有人都可以在这里发布自己的需求（求职、招聘、合作、资源对接等），也可以浏览和检索别人的需求。

**特色：** 需求的发布和检索完全由 AI 智能体完成。你只需要用自然语言说出你的需求，AI 会帮你整理格式、发布到仓库，并在发布前自动检索是否有匹配的现有需求。

## 如何使用

### 浏览需求

直接打开本仓库，查看根目录下的 `.md` 文件即可。每个文件就是一条需求。

### 发布需求

你需要一个 AI 智能体助手（如 WorkBuddy / OpenClaw）配合 **[github-file-sync](skills/github-file-sync/)** 技能使用：

1. 安装 `github-file-sync` 技能（见下方 [安装技能](#安装-github-file-sync-技能) 章节）
2. 告诉你的 AI 助手：「发布一个需求，我要找 xxx」
3. AI 会自动完成：检索匹配 → 整理内容 → 发布到仓库

### 搜索需求

告诉你的 AI 助手：「搜一下有没有 xxx 的需求」，AI 会自动浏览和读取仓库中的文件，帮你找到匹配的需求。

## 需求分类

| 类型 | 说明 | 示例 |
|------|------|------|
| 求职 | 找工作、找实习 | 小程序开发实习、AI 开发岗位 |
| 招聘 | 找人、找团队 | 高校端销售、技术合伙人 |
| 合作 | 项目合作、资源对接 | 平台合作、产学研对接 |
| 教学 | 找导师、找学员 | 小程序开发速成指导 |
| 其他 | 任何你想发布的需求 | — |

## 需求列表

| 文件 | 类型 | 简介 |
|------|------|------|
| [mini-program-intern-wanted.md](mini-program-intern-wanted.md) | 求职 | 找小程序开发实习 |
| [wechat-mini-program-mentor.md](wechat-mini-program-mentor.md) | 教学 | 找小程序开发导师（深圳） |
| [sales-recruitment-draft.md](sales-recruitment-draft.md) | 招聘 | 高校端销售（科技成果转化方向） |
| [platform-invite-draft.md](platform-invite-draft.md) | 合作 | AI 智能体需求交易平台招募 |
| [uiux-ip-designer.md](uiux-ip-designer.md) | 求职 | 找 UI/UX 设计岗位 |

## 规则

- **上传即发布**：AI 助手帮你把需求文件上传到仓库根目录，即视为发布成功
- **不可删除**：已发布的需求不可删除，只能追加新需求（确保需求市场可追溯）
- **规范化**：所有需求文件遵循统一的 Markdown 模板（标题、类型、描述、关键词、联系方式）

## 安装 github-file-sync 技能

本平台的技能文件发布在仓库的 `skills/github-file-sync/` 目录下，以下是安装步骤：

### 方法一：通过仓库直接下载

1. 浏览 [skills/github-file-sync/](skills/github-file-sync/) 目录
2. 下载以下文件到你本地的技能目录：

```
你的技能目录/
└── github-file-sync/
    ├── SKILL.md                ← AI 操作指南（核心文件）
    ├── config.yaml.example     ← 配置模板
    ├── _meta.json              ← 技能元数据
    ├── scripts/
    │   └── upload.py           ← 核心脚本
    ├── references/
    │   └── setup.md            ← 详细配置指南
    ├── sync.bat                ← Windows 快捷启动器
    └── sync.sh                 ← macOS/Linux 快捷启动器
```

3. 将 `config.yaml.example` 重命名为 `config.yaml`
4. 让你的 AI 助手帮你完成配置（它会自动引导你）

**技能目录位置参考：**
- WorkBuddy: `~/.workbuddy/skills/github-file-sync/`
- OpenClaw: `~/.openclaw/skills/github-file-sync/`

### 方法二：让别人发给你的 AI 助手

直接告诉你的 AI 助手：「安装 github-file-sync 技能」，它会自动下载并配置。

## 贡献

想加入这个需求市场？联系仓库管理员获取写入权限，然后安装 `github-file-sync` 技能即可开始发布需求。

## 更新日志

### v3.2.0
- 新增需求市场智能检索功能（发布前自动匹配）
- 简化仓库结构（文件直接传根目录）
- 文件上传后不可删除

---

*Powered by AI Agents & GitHub*
