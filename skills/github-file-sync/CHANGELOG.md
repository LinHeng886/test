# 更新日志

所有重要更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [3.2.0] - 2026-04-28

### 新增
- **需求市场功能**：发布需求前自动检索已有需求，匹配反馈给用户
- `upload.py check` 命令：输出 JSON 格式环境检测，AI 解析后自动引导配置
- SKILL.md 重写为 AI 自引导操作手册，安装后 AI 自动引导用户完成配置

### 变更
- 简化仓库结构：去掉 `users/{name}/` 多用户目录隔离，文件直接传根目录
- `config.yaml.example` 改为通用占位符（owner/repo 留空）
- `_meta.json` 描述更新

### 移除
- 删除 `delete` 子命令和 `delete_remote_file()` 函数（文件上传后不可删除）
- 移除多用户路径校验函数（`validate_user_path` 等）

---

## [3.0.0] - 2026-04-28

### 新增
- 初始版本
- GitHub API 模式：通过 Personal Access Token 直接上传文件
- 支持上传、浏览、读取、索引功能
- 交互式配置（`setup-user`）
- Windows / macOS / Linux 快捷启动器

---
