# GitHub File Sync — 文件共享工具

> 将本地 .md 文件上传到 GitHub 仓库，所有人打开仓库就能直接看到。
> 不依赖任何 AI 框架，只要有 Python 3 就能用。

## 快速开始

### 如果使用 AI 助手（推荐）

1. 把 `github-file-sync` 文件夹安装到你的 AI 框架技能目录
2. 跟你的 AI 助手说：**"帮我配置 GitHub 文件同步"**
3. AI 会自动引导你完成所有设置

### 如果只用命令行

#### 1. 安装依赖

```bash
pip install pyyaml
```

#### 2. 初始化配置

```bash
python scripts/upload.py setup-user
```

按提示填写 GitHub Token、仓库信息。

> **如何获取 GitHub Token？**
> 1. 打开 https://github.com/settings/tokens
> 2. 点击 **Generate new token (classic)**
> 3. 勾选 **repo** 权限
> 4. 生成后复制 Token

#### 3. 使用

```bash
python scripts/upload.py upload "我的笔记.md"
python scripts/upload.py upload --all "./文档/"
python scripts/upload.py browse
python scripts/upload.py read notes.md
python scripts/upload.py index
python scripts/upload.py check
```

---

## 所有命令

| 命令 | 说明 |
|------|------|
| `upload <文件>` | 上传单个 .md 文件 |
| `upload --all <目录>` | 批量上传目录下所有 .md |
| `browse` | 浏览仓库所有文件 |
| `read <路径>` | 读取文件内容 |
| `index` | 生成/更新文件索引 |
| `setup-user` | 初始化配置 |
| `check` | 检查配置状态 |

> 注意：文件上传后不可删除，只能追加。

---

## 仓库结构

上传的文件直接放在仓库根目录，打开就能看到：

```
your-repo/
├── notes.md          ← 上传的文件
├── 会议记录.md
└── _index.md         ← 自动索引
```

---

## 邀请新用户

1. 把 `github-file-sync` 文件夹发给对方
2. **不要发你的 `config.yaml`**（里面有 Token！）
3. 让对方把 `config.yaml.example` 重命名为 `config.yaml`
4. 对方的 AI 会自动引导配置
5. 在仓库 Settings → Collaborators 把对方加为协作者（Write 权限）

---

## 环境要求

- Python 3.7+
- `pyyaml`（`pip install pyyaml`）
- 一个 GitHub 账号
- 一个目标仓库
