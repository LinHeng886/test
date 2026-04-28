# GitHub File Sync — 详细配置指南

## 目录

1. [环境准备](#环境准备)
2. [配置方式：GitHub API 模式](#配置方式github-api-模式)
3. [配置验证](#配置验证)
4. [常见问题](#常见问题)

---

## 环境准备

### Python 依赖

```bash
pip install pyyaml
```

> 脚本内置使用 `urllib`（Python 标准库），`pyyaml` 仅用于读取配置文件。

### Windows 路径注意

脚本会自动将 Windows 路径（`C:\Users\...`）转换为 GitHub 路径（`C/Users/...`），
无需手动处理。

---

## 配置方式：GitHub API 模式

### 原理

通过 GitHub REST API (v3) 直接操作仓库文件，无需本地克隆仓库。
每个文件上传对应一次 `PUT /repos/{owner}/{repo}/contents/{path}` API 调用。

### 优点

- 无需本地存储仓库，任何有网络和 Token 的设备都能用
- 不占用本地磁盘空间
- 支持跨设备使用（同一 Token 即可）

### 缺点

- 需要生成并保管 GitHub Personal Access Token
- 单次只能上传/更新一个文件（GitHub API 限制）
- 不支持原子提交多个文件变更

### Step 1: 生成 GitHub Personal Access Token

1. 打开 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 填写 Note，例如：`github-file-sync`
4. 勾选权限范围：
   - `repo` — **Full control of private repositories**（必需，用于访问仓库）
5. 点击 **Generate token**
6. **立即复制 Token**（关闭页面后无法再次查看）

### Step 2: 填写配置

将 `config.yaml.example` 重命名为 `config.yaml`，然后填写：

```yaml
github:
  token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # 粘贴你的 Token
  owner: "your-github-username"                          # 你的 GitHub 用户名
  repo: "your-repo"                                     # 仓库名
  branch: "main"                                        # 分支名
  target_dir: ""                                        # 上传目标目录（留空=根目录）
  local_repo_path: ""
```

或者直接运行交互式配置：

```bash
python3 scripts/upload.py setup-user
```

### Step 3: 验证配置

```bash
# 检查配置状态
python3 scripts/upload.py check

# 测试上传（预览，不实际提交）
python3 scripts/upload.py upload "test.md" --dry-run

# 去掉 --dry-run 实际执行
python3 scripts/upload.py upload "test.md"
```

---

## 配置验证

### 快速测试

```bash
# 检查配置是否就绪（输出 JSON）
python3 scripts/upload.py check

# 浏览仓库文件
python3 scripts/upload.py browse

# Dry-run 测试上传
python3 scripts/upload.py upload "test.md" --dry-run
```

### 批量测试

```bash
# 批量上传整个目录（先 dry-run）
python3 scripts/upload.py upload --all "./docs/" --dry-run

# 确认无误后实际执行
python3 scripts/upload.py upload --all "./docs/"
```

---

## 常见问题

### Q1: 收到 `403 Forbidden`

**原因：** Token 权限不足或过期

**解决：**
1. 访问 https://github.com/settings/tokens 确认 Token 有效
2. 确保 Token 勾选了 `repo` 权限
3. 重新生成一个新 Token 并更新 `config.yaml`

### Q2: 收到 `404 Not Found`（上传时）

**原因（最常见）：** Token 对该仓库只有读权限，没有写权限。GitHub 对无写权限的写入请求统一返回 404。

**解决：**
1. 确认 Token 勾选了 `repo` 权限
2. 联系仓库所有者，将自己添加为协作者（Write 权限）：
   - 仓库页面 → Settings → Collaborators → Add people
   - 输入你的 GitHub 用户名 → 选择 Write 权限 → 发送邀请
3. 或换成一个你有写权限的仓库

### Q3: `check` 阶段报 `404`

**原因：** 仓库地址不对，或 Token 没有该仓库的任何权限

**解决：** 检查 `config.yaml` 中的 `owner` 和 `repo` 是否正确。

### Q4: Token 暴露了怎么办？

**立即行动：**
1. 访问 https://github.com/settings/tokens
2. 删除该 Token
3. 生成新 Token
4. 更新 `config.yaml`

### Q5: 文件上传后 GitHub 页面显示旧内容

**原因：** GitHub CDN 缓存

**解决：** 刷新页面，或在 URL 后加 `?ref=<branch>` 强制刷新

### Q6: Windows 路径问题

脚本已自动处理 Windows 路径（`\` → `/`），但注意：
- 路径中包含特殊字符（如 `#`、`!`、`$`）可能导致问题
- 建议使用双引号包裹路径
