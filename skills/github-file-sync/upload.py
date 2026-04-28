#!/usr/bin/env python3
"""
GitHub File Sync — 文件共享 & 需求发布助手

将本地 .md 文件上传到 GitHub 仓库，支持需求发布与智能检索。

用法:
    python3 upload.py upload <本地文件> [--message MSG] [--dry-run] [--verbose]
    python3 upload.py upload --all <本地目录> [--message MSG] [--dry-run]
    python3 upload.py browse [--verbose]
    python3 upload.py read <仓库文件路径>
    python3 upload.py index [--verbose]
    python3 upload.py setup-user
    python3 upload.py check
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR.parent / "config.yaml"
CONFIG = {}

# ─────────────────────────────────────────────────────────────────────────────
# 彩色输出
# ─────────────────────────────────────────────────────────────────────────────

def color(code, text):
    return f"\033[{code}m{text}\033[0m"

RED     = lambda t: color("1;31", t)
GREEN   = lambda t: color("1;32", t)
YELLOW  = lambda t: color("1;33", t)
BLUE    = lambda t: color("1;34", t)
CYAN    = lambda t: color("1;36", t)
DIM     = lambda t: color("2", t)
BOLD    = lambda t: color("1", t)


# ─────────────────────────────────────────────────────────────────────────────
# 配置加载
# ─────────────────────────────────────────────────────────────────────────────

def load_config():
    """加载 config.yaml"""
    global CONFIG
    if not CONFIG_PATH.exists():
        die(f"配置文件不存在: {CONFIG_PATH}\n请先运行: upload.py setup-user")
    try:
        import yaml
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            CONFIG = yaml.safe_load(f)
    except ImportError:
        die("需要 PyYAML，请运行: pip install pyyaml")

    gh = CONFIG.get("github", {})
    if not gh.get("owner") or not gh.get("repo"):
        die("config.yaml 中缺少 owner 或 repo 配置。")

    return gh


def die(msg):
    print(RED(f"\n  [错误] {msg}"))
    sys.exit(1)


def ok(msg):
    print(GREEN(f"  ✓ {msg}"))


def warn(msg):
    print(YELLOW(f"  ⚠ {msg}"))


def step(msg):
    print(f"\n{CYAN('▶')} {msg}")


def verbose(msg, force=False):
    if getattr(args, 'verbose', False) or force:
        print(DIM(f"    {msg}"))


# ─────────────────────────────────────────────────────────────────────────────
# GitHub API
# ─────────────────────────────────────────────────────────────────────────────

def github_api_request(method, url, token, data=None):
    """发送 GitHub API 请求"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-file-sync/3.0"
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    if data is not None and method.upper() in ("DELETE", "PUT", "PATCH"):
        req.method = method
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                result = {}
            return resp.status, result
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            return e.code, err_body
        except Exception:
            return e.code, {"message": str(e)}


def get_file_sha(token, owner, repo, branch, path):
    """获取 GitHub 上文件的 SHA"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    status, data = github_api_request("GET", f"{url}?ref={branch}", token)
    if status == 200 and isinstance(data, dict):
        return data.get("sha")
    return None


def get_file_content(token, owner, repo, branch, path):
    """获取 GitHub 上文件的内容（base64 解码）"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    status, data = github_api_request("GET", f"{url}?ref={branch}", token)
    if status == 200 and isinstance(data, dict):
        content_b64 = data.get("content", "")
        content_b64 = content_b64.replace("\n", "")
        try:
            return base64.b64decode(content_b64).decode("utf-8")
        except Exception:
            return None
    return None


def list_repo_tree(token, owner, repo, branch, path=""):
    """
    递归获取仓库目录树。
    返回: [{path, name, type, size, sha, download_url}]
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    status, data = github_api_request("GET", f"{url}?ref={branch}", token)

    if status == 404:
        return []
    if status != 200 or not isinstance(data, list):
        return []

    results = []
    for item in data:
        if item["type"] == "file":
            results.append({
                "path": item["path"],
                "name": item["name"],
                "type": "file",
                "size": item.get("size", 0),
                "sha": item.get("sha", ""),
                "download_url": item.get("download_url", ""),
            })
        elif item["type"] == "dir":
            sub_items = list_repo_tree(token, owner, repo, branch, item["path"])
            results.extend(sub_items)

    return results


def upload_file_api(token, owner, repo, branch, remote_path, content_bytes, message, sha=None):
    """通过 GitHub API 上传/更新文件"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote_path}"
    data = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("ascii"),
        "branch": branch
    }
    if sha:
        data["sha"] = sha

    status, resp = github_api_request("PUT", f"{url}?ref={branch}", token, data)
    if status in (200, 201):
        return True, resp.get("commit", {}).get("html_url", "")
    elif status == 422:
        return True, "(内容无变化，跳过)"
    else:
        return False, resp.get("message", f"HTTP {status}")


def delete_file_api(token, owner, repo, branch, remote_path, sha, message):
    """通过 GitHub API 删除文件（仅内部保留，不对外暴露）"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote_path}"
    data = {"message": message, "sha": sha, "branch": branch}
    status, resp = github_api_request("DELETE", f"{url}?ref={branch}", token, data)
    if status in (200, 204):
        return True, resp.get("commit", {}).get("html_url", "(已删除)")
    else:
        return False, resp.get("message", f"HTTP {status}")


# ─────────────────────────────────────────────────────────────────────────────
# 提交信息生成
# ─────────────────────────────────────────────────────────────────────────────

def generate_commit_message(action, filename):
    """生成 Conventional Commits 格式的提交信息"""
    templates = {
        "add":    f"feat: add {filename}",
        "update": f"fix: update {filename}",
    }
    return templates.get(action, f"{action}: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# 路径工具
# ─────────────────────────────────────────────────────────────────────────────

def get_target_dir():
    """获取上传目标目录前缀（可能为空字符串）"""
    return CONFIG.get("github", {}).get("target_dir", "").strip().rstrip("/")


def get_index_filename():
    """获取索引文件名"""
    return CONFIG.get("index", {}).get("filename", "_index.md")


def build_remote_path(filename):
    """
    构建完整的远程路径: target_dir/filename
    例如 target_dir="docs" → "docs/notes.md"
         target_dir="" → "notes.md"
    """
    target = get_target_dir()
    if target:
        return f"{target}/{filename}"
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# 上传逻辑
# ─────────────────────────────────────────────────────────────────────────────

def upload_single_file(local_path, message=None, dry_run=False):
    """上传单个文件到仓库"""
    gh = CONFIG["github"]
    token = gh.get("token", "").strip()
    owner = gh["owner"]
    repo = gh["repo"]
    branch = gh.get("branch", "main")

    filename = Path(local_path).name
    remote_path = build_remote_path(filename)

    commit_msg = message or generate_commit_message("add", filename)

    if dry_run:
        print(f"\n  {CYAN('[Dry Run]')} 上传文件:")
        print(f"    本地: {local_path}")
        print(f"    远程: {remote_path}")
        print(f"    提交: {commit_msg}")
        return

    if not token:
        die("未配置 GitHub Token。请在 config.yaml 中填写 github.token。")

    with open(local_path, "rb") as f:
        content = f.read()

    sha = get_file_sha(token, owner, repo, branch, remote_path)
    action = "update" if sha else "add"
    commit_msg = message or generate_commit_message(action, filename)

    success, result = upload_file_api(token, owner, repo, branch, remote_path, content, commit_msg, sha)
    if success:
        ok(f"已{'更新' if action == 'update' else '上传'} {filename} → {remote_path}")
        if result != "(内容无变化，跳过)":
            verbose(f"  提交: {result}")
    else:
        die(f"上传失败: {result}")


def batch_upload(local_dir, message=None, dry_run=False):
    """批量上传目录下所有 .md 文件"""
    gh = CONFIG["github"]
    token = gh.get("token", "").strip()
    owner = gh["owner"]
    repo = gh["repo"]
    branch = gh.get("branch", "main")

    local_dir = Path(local_dir).resolve()
    if not local_dir.exists():
        die(f"目录不存在: {local_dir}")

    md_files = []
    for root, _dirs, files in os.walk(local_dir):
        for fname in files:
            if fname.lower().endswith((".md", ".markdown")):
                md_files.append(Path(root) / fname)

    if not md_files:
        warn(f"在 {local_dir} 中未找到 .md 文件")
        return

    print(f"\n  找到 {len(md_files)} 个 .md 文件\n")

    target = get_target_dir()
    success_count = 0
    for fpath in sorted(md_files):
        rel = fpath.relative_to(local_dir)

        # 保留子目录结构
        if target:
            remote_path = f"{target}/{rel}"
        else:
            remote_path = str(rel)

        action = "add"
        commit_msg = message or generate_commit_message(action, str(rel))

        print(f"  {CYAN('→')} {rel}", end=" ... ")

        if dry_run:
            print(YELLOW("[Dry Run]") + DIM(f" → {remote_path}"))
            success_count += 1
            continue

        with open(fpath, "rb") as f:
            content = f.read()

        sha = get_file_sha(token, owner, repo, branch, remote_path)
        action = "update" if sha else "add"
        commit_msg = message or generate_commit_message(action, str(rel))

        success, result = upload_file_api(token, owner, repo, branch, remote_path, content, commit_msg, sha)
        if success:
            print(GREEN("✓") + DIM(f" → {remote_path}"))
            success_count += 1
        else:
            print(RED(f"✗ {result}"))

    print(f"\n  {GREEN(f'成功: {success_count}/{len(md_files)}')}")


# ─────────────────────────────────────────────────────────────────────────────
# 浏览/读取
# ─────────────────────────────────────────────────────────────────────────────

def browse_repo():
    """浏览仓库中所有 .md 文件"""
    gh = CONFIG["github"]
    token = gh.get("token", "").strip()
    owner = gh["owner"]
    repo = gh["repo"]
    branch = gh.get("branch", "main")
    index_file = get_index_filename()

    print(f"\n  {BOLD(f'GitHub 仓库文件浏览')}")
    print(f"  仓库: {CYAN(f'{owner}/{repo}')} (分支: {branch})\n")

    all_files = list_repo_tree(token, owner, repo, branch)
    if not all_files:
        warn("仓库为空，还没有任何文件")
        return

    # 过滤 .md 文件，排除索引文件
    md_files = [
        f for f in all_files
        if f["name"].lower().endswith((".md", ".markdown"))
        and f["name"] != index_file
    ]

    if not md_files:
        warn("没有找到 .md 文件")
        return

    for f in md_files:
        size_kb = f["size"] / 1024
        print(f"    {BLUE('📄')} {f['path']}  {DIM(f'({size_kb:.1f} KB)')}")

    print(f"\n  {DIM(f'共 {len(md_files)} 个文件')}")


def read_remote_file(remote_path):
    """读取仓库中的文件内容"""
    gh = CONFIG["github"]
    token = gh.get("token", "").strip()
    owner = gh["owner"]
    repo = gh["repo"]
    branch = gh.get("branch", "main")

    path = remote_path.replace("\\", "/").lstrip("/")
    verbose(f"读取: {path}")

    content = get_file_content(token, owner, repo, branch, path)
    if content is None:
        die(f"无法读取文件: {path}（可能不存在）")

    print(f"\n{CYAN('═' * 60)}")
    print(f"  {BOLD(path)}")
    print(f"  {DIM(f'{owner}/{repo} @ {branch}')}")
    print(f"{CYAN('═' * 60)}\n")
    print(content)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# 索引生成
# ─────────────────────────────────────────────────────────────────────────────

def generate_index():
    """生成仓库索引文件 _index.md"""
    gh = CONFIG["github"]
    token = gh.get("token", "").strip()
    owner = gh["owner"]
    repo = gh["repo"]
    branch = gh.get("branch", "main")
    index_name = get_index_filename()

    step("正在扫描仓库文件...")
    all_files = list_repo_tree(token, owner, repo, branch)

    # 过滤 .md 文件，排除索引文件自身
    md_files = [
        f for f in all_files
        if f["name"].lower().endswith((".md", ".markdown"))
        and f["name"] != index_name
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 文件索引",
        f"",
        f"> 自动生成于 {now} | [仓库地址](https://github.com/{owner}/{repo})",
        f"",
        f"---",
        f"",
    ]

    if md_files:
        for f in sorted(md_files, key=lambda x: x["path"]):
            lines.append(f"- [{f['path']}]({f['path']})")
        lines.append(f"")
    else:
        lines.append(f"*暂无文件*")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"*此索引由 github-file-sync 自动生成*")
    lines.append(f"")

    index_content = "\n".join(lines)
    verbose(f"索引内容长度: {len(index_content)} 字符")

    sha = get_file_sha(token, owner, repo, branch, index_name)
    action = "update" if sha else "add"
    commit_msg = f"docs: update index ({len(md_files)} files)"

    content_bytes = index_content.encode("utf-8")
    success, result = upload_file_api(token, owner, repo, branch, index_name, content_bytes, commit_msg, sha)

    if success:
        ok(f"索引已{'更新' if action == 'update' else '创建'}: {index_name}")
        verbose(f"  {result}")
    else:
        die(f"索引上传失败: {result}")


# ─────────────────────────────────────────────────────────────────────────────
# 用户初始化
# ─────────────────────────────────────────────────────────────────────────────

def setup_user():
    """初始化用户配置（交互式）"""
    print(f"\n{CYAN('═' * 50)}")
    print(f"  {BOLD('GitHub File Sync — 初始化配置')}")
    print(f"{CYAN('═' * 50)}")

    # 如果配置已存在，读取已有信息
    if CONFIG_PATH.exists():
        try:
            import yaml
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}
        except Exception:
            existing = {}
    else:
        existing = {}

    gh = existing.get("github", {})

    print()
    token = gh.get("token", "").strip()
    if not token:
        token = input(f"  {CYAN('1.')} GitHub Personal Access Token: ").strip()
    else:
        print(f"  {CYAN('1.')} GitHub Token: {DIM('已配置 (' + token[:8] + '...)')}")

    owner = gh.get("owner", "").strip()
    if not owner:
        owner = input(f"  {CYAN('2.')} GitHub 用户名/组织名: ").strip()
    else:
        print(f"  {CYAN('2.')} 仓库所有者: {owner}")

    repo = gh.get("repo", "").strip()
    if not repo:
        repo = input(f"  {CYAN('3.')} 仓库名: ").strip()
    else:
        print(f"  {CYAN('3.')} 仓库名: {repo}")

    branch = gh.get("branch", "main").strip()
    target_dir = gh.get("target_dir", "").strip()
    if not target_dir:
        target_input = input(f"  {CYAN('4.')} 上传目标目录（直接回车=仓库根目录）: ").strip()
        target_dir = target_input
    else:
        print(f"  {CYAN('4.')} 目标目录: {target_dir or '(根目录)'}")

    # 构建配置
    config = {
        "github": {
            "token": token,
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "target_dir": target_dir,
            "local_repo_path": "",
        },
        "index": {
            "filename": "_index.md",
        },
    }

    # 保存配置
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        import yaml
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n  {GREEN('✓ 配置已保存')}: {CONFIG_PATH}")
    print(f"\n  {BOLD('仓库地址')}: {CYAN(f'https://github.com/{owner}/{repo}')}")
    print(f"  {BOLD('上传目录')}: {CYAN(target_dir or '(根目录)')}")
    print(f"\n  {DIM('现在可以使用以下命令:')}")
    print(f"    {DIM('upload notes.md         # 上传文件')}")
    print(f"    {DIM('browse                  # 浏览所有文件')}")
    print(f"    {DIM('read notes.md           # 读取文件内容')}")
    print(f"    {DIM('index                   # 生成索引')}")


# ─────────────────────────────────────────────────────────────────────────────
# 配置检查
# ─────────────────────────────────────────────────────────────────────────────

def check_setup():
    """
    检查当前环境配置状态，输出 JSON 格式的检测结果。
    """
    results = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "pyyaml_installed": False,
        "config_exists": False,
        "config_valid": False,
        "token_set": False,
        "owner_set": False,
        "repo_set": False,
        "api_ok": False,
        "api_error": None,
        "repo_url": "",
        "target_dir": "",
        "issues": [],
        "ready": False,
    }

    # 1. 检查 pyyaml
    try:
        import yaml
        results["pyyaml_installed"] = True
    except ImportError:
        results["issues"].append("pyyaml 未安装，请运行: pip install pyyaml")

    # 2. 检查配置文件
    if CONFIG_PATH.exists():
        results["config_exists"] = True
        if results["pyyaml_installed"]:
            try:
                import yaml
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
            except Exception as e:
                results["issues"].append(f"config.yaml 解析失败: {e}")
                print(json.dumps(results, ensure_ascii=False, indent=2))
                return

            gh = cfg.get("github", {})

            token = gh.get("token", "").strip()
            owner = gh.get("owner", "").strip()
            repo = gh.get("repo", "").strip()

            if token:
                results["token_set"] = True
            else:
                results["issues"].append("未配置 GitHub Token")

            if owner:
                results["owner_set"] = True
            else:
                results["issues"].append("未配置仓库所有者 (github.owner)")

            if repo:
                results["repo_set"] = True
            else:
                results["issues"].append("未配置仓库名 (github.repo)")

            results["config_valid"] = all([results["token_set"], results["owner_set"],
                                            results["repo_set"]])

            if results["config_valid"]:
                branch = gh.get("branch", "main")
                results["target_dir"] = gh.get("target_dir", "")
                results["repo_url"] = f"https://github.com/{owner}/{repo}"

                # 测试 API 连通性
                url = f"https://api.github.com/repos/{owner}/{repo}"
                status, data = github_api_request("GET", url, token)
                if status == 200:
                    results["api_ok"] = True
                else:
                    results["api_error"] = data.get("message", f"HTTP {status}")
                    if status == 401:
                        results["issues"].append(f"Token 无效或已过期: {results['api_error']}")
                    elif status == 404:
                        results["issues"].append(f"仓库不存在或无权限: {owner}/{repo}")
                    else:
                        results["issues"].append(f"API 错误: {results['api_error']}")

                results["ready"] = results["api_ok"]
    else:
        results["issues"].append("config.yaml 不存在，需要运行: upload.py setup-user")

    print(json.dumps(results, ensure_ascii=False, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# 主程序入口
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global args
    parser = argparse.ArgumentParser(
        description="GitHub File Sync — 文件共享助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    upload.py upload notes.md                    上传文件
  upload.py upload --all ./docs/               批量上传目录
  upload.py browse                             浏览仓库所有文件
  upload.py read notes.md                      读取仓库中的文件
  upload.py index                              生成/更新文件索引
  upload.py setup-user                         初始化配置
  upload.py check                              检查配置状态
        """
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # upload
    p = sub.add_parser("upload", help="上传文件到仓库")
    p.add_argument("path", nargs="?", help="本地文件或目录路径")
    p.add_argument("--all", action="store_true", help="批量上传目录下所有 .md 文件")
    p.add_argument("--message", "-m", help="自定义提交信息")
    p.add_argument("--dry-run", action="store_true", help="模拟运行（不实际提交）")
    p.add_argument("--verbose", "-v", action="store_true")

    # browse
    p = sub.add_parser("browse", help="浏览仓库中所有 .md 文件")
    p.add_argument("--verbose", "-v", action="store_true")

    # read
    p = sub.add_parser("read", help="读取仓库中的文件内容")
    p.add_argument("path", help="仓库中的文件路径")
    p.add_argument("--verbose", "-v", action="store_true")

    # index
    p = sub.add_parser("index", help="生成/更新仓库文件索引")
    p.add_argument("--verbose", "-v", action="store_true")

    # setup-user
    p = sub.add_parser("setup-user", help="初始化配置")
    p.add_argument("--verbose", "-v", action="store_true")

    # check
    p = sub.add_parser("check", help="检查配置状态（输出 JSON）")
    p.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.command == "setup-user":
        setup_user()
        return

    if args.command == "check":
        check_setup()
        return

    # 以下命令都需要加载配置
    load_config()

    if args.command == "upload":
        if not args.path and not args.all:
            print(f"\n  {GREEN('用法:')}")
            print(f"    upload notes.md              # 上传单个文件")
            print(f"    upload --all ./docs/         # 批量上传目录")
            print(f"    upload notes.md --dry-run    # 预览")
            return
        if args.all:
            batch_upload(args.path, args.message, args.dry_run)
        else:
            upload_single_file(args.path, args.message, args.dry_run)

    elif args.command == "browse":
        browse_repo()

    elif args.command == "read":
        read_remote_file(args.path)

    elif args.command == "index":
        generate_index()


if __name__ == "__main__":
    main()
