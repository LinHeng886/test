#!/usr/bin/env bash
# GitHub File Sync — macOS/Linux 快捷启动器
# 用法: chmod +x sync.sh && ./sync.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 查找 Python
PYTHON=""
command -v python3 &>/dev/null && PYTHON="python3"
command -v python &>/dev/null && PYTHON="python"

if [ -z "$PYTHON" ]; then
    echo "[错误] 未找到 Python，请先安装 Python 3.7+"
    exit 1
fi

# 检查依赖
$PYTHON -c "import yaml" 2>/dev/null || {
    echo "[提示] 正在安装依赖 pyyaml..."
    $PYTHON -m pip install pyyaml
}

# 检查是否已配置
if [ ! -f "$SCRIPT_DIR/config.yaml" ]; then
    $PYTHON "$SCRIPT_DIR/scripts/upload.py" setup-user
    exit 0
fi

# 没有参数时直接传帮助
if [ $# -eq 0 ]; then
    $PYTHON "$SCRIPT_DIR/scripts/upload.py" --help
    exit 0
fi

# 传递参数
$PYTHON "$SCRIPT_DIR/scripts/upload.py" "$@"
