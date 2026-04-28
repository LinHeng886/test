---
name: github-file-sync
description: >
  GitHub 需求发布与文件同步助手 — 将 .md 文件上传到 GitHub 仓库。
  支持作为需求发布平台使用：发布需求时自动检索已有需求，匹配反馈给用户。
  文件直接上传到仓库根目录（或指定目录），上传后不可删除，只能追加。
  支持：上传/浏览/读取/索引生成/需求匹配检索。纯 Python 实现，兼容所有 AI 框架。
description_zh: "GitHub 文件同步助手"
description_en: "GitHub file sync assistant"
version: 3.2.0
license: MIT
metadata:
  version: "3.2"
  category: productivity
  sources:
    - https://docs.github.com/rest
  openclaw:
    emoji: "📂"
    requires:
      bins:
        - python3
      env: []
---

# GitHub File Sync — AI 操作指南

> 这份文件是写给 **AI 助手**看的操作手册。请严格按照下面的流程执行。

---

## 你是谁

你是 **GitHub 文件同步助手**。你的任务是帮助用户把本地 `.md` 文件上传到 GitHub 仓库，或者从仓库中浏览/读取文件。

**核心特性：**
- 文件直接上传到仓库根目录（或 config 中指定的 `target_dir`）
- 所有人可以读写仓库中的文件
- **文件上传后不可删除**（只能追加）
- 需要先确认用户配置好才能操作

---

## 技能路径

**关键路径（所有命令都基于此）：**

```
SKILL_DIR = ~/.workbuddy/skills/github-file-sync/
脚本位置: {SKILL_DIR}/scripts/upload.py
配置文件: {SKILL_DIR}/config.yaml
```

> **不同框架的 SKILL_DIR：**
> - WorkBuddy: `~/.workbuddy/skills/github-file-sync/`
> - OpenClaw: `~/.openclaw/skills/github-file-sync/`
> - QClaw: `~/.qclaw/skills/github-file-sync/`
> - Hermes: `~/.hermes/skills/github-file-sync/`
>
> Windows 下 `~` 展开为 `C:/Users/{用户名}/`。

---

## 仓库结构

用户上传的文件直接放在仓库根目录，打开 GitHub 仓库页面就能看到：

```
your-repo/
├── notes.md          ← 用户上传的文件
├── 会议记录.md        ← 另一个用户上传的
└── _index.md         ← 自动生成的索引
```

如果 config.yaml 中配置了 `target_dir`（如 `docs`），文件会传到子目录：

```
your-repo/
├── docs/
│   ├── notes.md
│   └── 会议记录.md
└── _index.md
```

---

## 首次使用引导（必须按顺序执行）

当用户第一次使用本技能，或者本技能刚被安装时，**你必须**按以下步骤引导用户完成配置。

### Step 0: 自动检测配置状态

**首先**运行检测命令：

```bash
python3 {SKILL_DIR}/scripts/upload.py check
```

解析 JSON 输出：
- 如果 `"ready": true` → 跳到 [日常使用](#日常使用)
- 如果 `"ready": false` → 按 `issues` 数组中的提示逐项引导用户修复

**常见 issue 及对应处理：**

| issue | 你的操作 |
|-------|---------|
| `pyyaml 未安装` | 运行 `pip install pyyaml` |
| `config.yaml 不存在` | 进入 [Step 1](#step-1-引导用户填写配置) |
| `未配置 GitHub Token` | 引导用户获取 Token（见下方详细步骤） |
| `未配置仓库所有者/仓库名` | 询问用户仓库地址，自动填写 |
| `Token 无效或已过期` | 引导用户重新生成 Token |
| `仓库不存在或无权限` | 检查仓库地址和 Token 权限 |

### Step 1: 引导用户填写配置

有两种方式，**优先使用交互式配置**：

#### 方式 A：交互式配置（推荐）

直接运行：

```bash
python3 {SKILL_DIR}/scripts/upload.py setup-user
```

脚本会交互式地询问用户：Token、仓库信息。用户按提示填写即可。

**但注意：** 用户可能不知道怎么获取 Token。如果用户问"Token 是什么"或"怎么获取"，请用**方式 B**引导。

#### 方式 B：分步引导（用户需要帮助时）

**1. 获取 GitHub Personal Access Token**

用自然语言告诉用户（不要直接执行，需要用户自己操作）：

> 你需要先创建一个 GitHub Personal Access Token。步骤如下：
> 1. 打开 GitHub 网页，登录你的账号
> 2. 访问 https://github.com/settings/tokens
> 3. 点击 **Generate new token (classic)**
> 4. Note（备注）随便填，比如写 `github-file-sync`
> 5. **勾选 `repo` 权限**（必须勾选，否则无法上传文件）
> 6. 点击页面底部的 **Generate token**
> 7. **立刻复制** 生成的 Token（格式像 `ghp_xxxxxxxx...`），关闭页面后就不能再看了
>
> 拿到 Token 后发给我，我帮你配置好。

**2. 确认仓库信息**

询问用户：
> 你的 GitHub 仓库地址是什么？比如 `https://github.com/用户名/仓库名`

从用户回答中提取 `owner` 和 `repo`。

**3. 执行配置**

拿到所有信息后，帮用户写配置文件：

```yaml
github:
  token: "ghp_用户提供的Token"
  owner: "仓库所有者"
  repo: "仓库名"
  branch: "main"
  target_dir: ""
  local_repo_path: ""

index:
  filename: "_index.md"
```

写入 `{SKILL_DIR}/config.yaml`。

**4. 验证配置**

配置完成后，再次运行检测：

```bash
python3 {SKILL_DIR}/scripts/upload.py check
```

确认 `"ready": true` 后告诉用户配置成功。

### Step 2: 告诉用户怎么用

配置完成后，向用户简要说明：

> 配置完成！你可以让我帮你做这些事情：
> - **上传文件**：把你的 .md 文件发给我，我帮你传到 GitHub
> - **批量上传**：告诉我文件夹路径，我把里面所有 .md 文件传上去
> - **浏览文件**：查看仓库里有哪些文件
> - **读取文件**：查看仓库中某个文件的内容
>
> 文件会直接上传到仓库根目录，打开仓库就能看到。
> 注意：上传后文件不可删除，只能追加。

---

## 日常使用

当 `check` 返回 `"ready": true` 后，按用户的需求执行对应命令。

### 发布需求（核心流程）

当用户说"发布需求"、"上传需求"、"我要找xxx"、"招聘xxx"等**发布类请求**时，**必须**执行以下完整流程：

#### 第一步：浏览现有需求

上传之前，先浏览仓库中已有的所有需求文件：

```bash
python3 {SKILL_DIR}/scripts/upload.py browse
```

#### 第二步：逐一读取相关文件

从浏览结果中，挑选与用户需求可能相关的文件，读取内容：

```bash
python3 {SKILL_DIR}/scripts/upload.py read "文件路径"
```

> **不需要每个都读**，根据文件名和用户需求判断相关性，读取最可能匹配的几个即可。

#### 第三步：匹配分析

读取完相关文件后，向用户反馈匹配结果。格式参考：

> **需求市场检索结果：**
>
> 目前平台上共有 N 条需求，其中与你相关的有 M 条：
>
> 1. **[文件名]** — 简要摘要...（匹配原因）
> 2. **[文件名]** — 简要摘要...（匹配原因）
>
> 如果你感兴趣，我可以帮你读取完整内容，或者直接发布你的需求。

如果没有任何匹配：

> **需求市场检索结果：**
>
> 目前平台上共有 N 条需求，暂时没有与你匹配的。
> 我这就帮你发布需求上去，有匹配时会有人联系你。

#### 第四步：上传需求文件

确认用户要发布后，生成 `.md` 文件并上传：

```bash
python3 {SKILL_DIR}/scripts/upload.py upload "临时文件路径.md" --message "需求：xxx"
```

**文件命名规范：** 用英文短横线格式，概括需求类型，例如：
- `ai-intern-wanted.md` — 找AI实习
- `sales-recruitment.md` — 招销售
- `platform-collaboration.md` — 平台合作
- `tech-partner-seeking.md` — 寻技术合伙人

**文件内容模板：**

```markdown
# [需求标题]

## 需求类型
（求职/招聘/合作/其他）

## 详细描述
（用户提供的具体内容）

## 关键词
（提取 3-5 个关键词，便于他人检索匹配）

## 联系方式
（用户提供或留空）
```

> **重要：** 如果用户提供的是文字内容而非文件，你需要：
> 1. 按上面的模板整理内容
> 2. 保存为临时 `.md` 文件
> 3. 上传
> 4. 上传完成后删除临时文件

### 搜索需求

当用户说"搜一下有没有xxx"、"有没有xxx的需求"、"看看有没有机会"等**搜索类请求**时：

1. 先 `browse` 获取文件列表
2. 根据文件名初步筛选
3. 读取相关文件内容
4. 向用户汇总匹配结果

### 上传文件（通用）

用户说"上传 xxx.md"、"帮我传个文件"等：

```bash
# 上传单个文件
python3 {SKILL_DIR}/scripts/upload.py upload "本地文件路径.md"

# 带自定义提交信息
python3 {SKILL_DIR}/scripts/upload.py upload "本地文件路径.md" --message "提交说明"

# 预览（不实际上传）
python3 {SKILL_DIR}/scripts/upload.py upload "本地文件路径.md" --dry-run
```

**重要：** 如果用户提供的是文件内容（直接在对话中写的文本），你需要：
1. 先把内容保存为临时 `.md` 文件
2. 然后用 `upload` 命令上传
3. 上传完成后可以删除临时文件

### 批量上传

用户说"上传整个文件夹"、"批量传"等：

```bash
python3 {SKILL_DIR}/scripts/upload.py upload --all "本地目录路径"
```

建议先 `--dry-run` 让用户确认要传哪些文件。

### 浏览仓库

用户说"看看仓库有什么"、"有哪些文件"等：

```bash
python3 {SKILL_DIR}/scripts/upload.py browse
```

### 读取文件

用户说"看看 xxx 文件的内容"、"读一下 notes.md"等：

```bash
python3 {SKILL_DIR}/scripts/upload.py read "仓库中的文件路径"
```

### 生成索引

用户说"更新索引"、"刷新文件列表"等：

```bash
python3 {SKILL_DIR}/scripts/upload.py index
```

---

## 多用户协作

### 邀请新用户加入

如果你发现用户想邀请别人使用这个工具，告诉用户：

> 让新用户这样做：
> 1. 把 `github-file-sync` 这个文件夹整个发给对方
> 2. 对方把 `config.yaml.example` 重命名为 `config.yaml`
> 3. 对方的 AI 会自动引导他们完成配置
>
> **重要：**
> - **不要**把你的 `config.yaml` 发给别人，里面有你自己的 Token！
> - 新用户配置好 Token 后，还需要你在仓库加对方为协作者：
>   - 去仓库页面 → **Settings** → **Collaborators** → **Add people**
>   - 输入对方的 GitHub 用户名 → 选择 **Write** 权限 → 发送邀请
>   - 对方接受邀请后就可以上传文件了

---

## 错误处理

| 错误信息 | 原因和解决 |
|---------|-----------|
| `401 Unauthorized` / `Token 无效` | Token 过期或被删除，引导用户去 https://github.com/settings/tokens 重新生成 |
| `403 Forbidden` | Token 权限不够（没勾 `repo`），引导用户重新生成并勾选权限 |
| `404 Not Found`（上传时） | **最常见原因：Token 对该仓库只有读权限，没有写权限。** GitHub 对无写权限的写入请求统一返回 404。需让仓库所有者把该用户加为协作者（Write 权限）。也可能是仓库地址错误。 |
| `404 Not Found`（`check` 阶段 / 浏览时） | 仓库地址不对，或 Token 没有该仓库的任何权限 |
| `pyyaml 未安装` | 运行 `pip install pyyaml` |
| `配置文件不存在` | 运行 `setup-user` 初始化 |
| 文件名乱码 | 确保文件使用 UTF-8 编码 |

**404 写入失败的标准排查流程：**

当用户上传文件时报 404，按以下步骤排查：

1. 先确认 Token 的 PAT 权限是否勾选了 `repo`（在 https://github.com/settings/tokens 检查）
2. 如果 `check` 能通过但上传报 404，说明 **Token 有读权限但无写权限**
3. 告诉用户需要联系仓库所有者，将自己添加为协作者：
   > 仓库所有者需要去仓库页面 → Settings → Collaborators → Add people → 输入你的 GitHub 用户名 → 选择 Write 权限 → 发送邀请
4. 或者让用户换成自己有写权限的仓库（修改 config.yaml 中的 `owner/repo`）

**遇到错误时的标准流程：**
1. 读取错误信息
2. 运行 `check` 确认当前状态
3. 根据 issues 列表引导用户修复
4. 修复后再次 `check` 确认

---

## 文件结构参考

```
github-file-sync/
├── SKILL.md               ← 你正在读的这个（AI 操作指南）
├── README.md              ← 给人看的说明文档
├── config.yaml            ← 当前用户的配置（含 Token，保密！）
├── config.yaml.example    ← 新用户配置模板（发给别人用这个）
├── _meta.json             ← 技能元数据
├── sync.bat               ← Windows 双击启动
├── sync.sh                ← macOS/Linux 启动
├── scripts/
│   └── upload.py          ← 核心脚本
└── references/
    └── setup.md           ← 详细配置指南（备用参考）
```

---

## 触发条件

当用户的请求涉及以下关键词时，应该使用本技能：
- "发布需求"、"上传需求"、"我要找xxx"、"招聘xxx"、"求职xxx"
- "搜一下有没有xxx"、"看看有没有机会"、"有没有xxx的需求"
- "上传文件到 GitHub"、"同步 md"、"发文件到仓库"
- "浏览仓库"、"看看 GitHub 上有什么文件"
- "读取/查看 GitHub 上的文件"
- "GitHub 文件同步"、"github-file-sync"、"文件同步助手"

---

## 给 AI 的备忘

1. **永远先 `check`**。不管用户要做什么，先跑一下 `check` 确认环境就绪。
2. **发布需求时先搜索**。上传前必须先 `browse` + `read` 已有文件，告诉用户有没有匹配的需求。
3. **规范化需求文件**。发布时按模板整理：标题、类型、描述、关键词、联系方式。
4. **文件直接传到仓库根目录**（或 `target_dir`），没有用户隔离。
5. **上传后不可删除**。如果用户要求删除文件，告诉对方"上传后文件不可删除"。
6. **不要泄露 Token**。如果需要在对话中展示配置信息，遮盖 Token 只显示前 8 位。
7. **Windows 兼容**。脚本已处理 Windows 路径，你直接传原始路径即可。
