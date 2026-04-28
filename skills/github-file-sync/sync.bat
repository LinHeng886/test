@echo off
chcp 65001 >nul 2>&1
setlocal

:: GitHub File Sync — Windows 快捷启动器
:: 双击运行，或在终端输入 sync

set "SCRIPT_DIR=%~dp0"
set "PYTHON="

:: 查找 Python
where python3 >nul 2>&1 && set "PYTHON=python3"
where python >nul 2>&1 && set "PYTHON=python"
if "%PYTHON%"=="" (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖
%PYTHON% -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖 pyyaml...
    %PYTHON% -m pip install pyyaml
)

:: 检查是否已配置
if not exist "%SCRIPT_DIR%config.yaml" (
    echo.
    echo ════════════════════════════════════════════
    echo   GitHub File Sync — 首次使用
    echo ════════════════════════════════════════════
    echo.
    %PYTHON% "%SCRIPT_DIR%scripts\upload.py" setup-user
    pause
    exit /b 0
)

:: 没有参数时显示菜单
if "%~1"=="" (
    echo.
    echo ════════════════════════════════════════════
    echo   GitHub File Sync
    echo ════════════════════════════════════════════
    echo.
    echo   1. 上传文件
    echo   2. 批量上传目录
    echo   3. 浏览所有文件
    echo   4. 读取文件
    echo   5. 生成索引
    echo   6. 检查配置状态
    echo   0. 退出
    echo.
    set /p choice="  请选择 (0-6): "

    if "%choice%"=="1" (
        set /p filepath="  输入文件路径: "
        %PYTHON% "%SCRIPT_DIR%scripts\upload.py" upload "!filepath!"
    ) else if "%choice%"=="2" (
        set /p dirpath="  输入目录路径: "
        %PYTHON% "%SCRIPT_DIR%scripts\upload.py" upload --all "!dirpath!"
    ) else if "%choice%"=="3" (
        %PYTHON% "%SCRIPT_DIR%scripts\upload.py" browse
    ) else if "%choice%"=="4" (
        set /p filepath="  输入文件路径: "
        %PYTHON% "%SCRIPT_DIR%scripts\upload.py" read "!filepath!"
    ) else if "%choice%"=="5" (
        %PYTHON% "%SCRIPT_DIR%scripts\upload.py" index
    ) else if "%choice%"=="6" (
        %PYTHON% "%SCRIPT_DIR%scripts\upload.py" check
    )
    echo.
    pause
    exit /b 0
)

:: 有参数时直接传递给脚本
%PYTHON% "%SCRIPT_DIR%scripts\upload.py" %*
