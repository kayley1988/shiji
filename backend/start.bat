@echo off
cd /d E:\shiji\backend

REM ===========================================
REM 诗语雅集 - 后端启动脚本 (安全版)
REM ===========================================

REM 加载 .env 文件中的配置
if exist .env (
    echo 加载 .env 配置...
    for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
)

REM 设置默认值（如果 .env 中未设置）
if not defined SECRET_KEY (
    echo 设置默认 SECRET_KEY...
    set SECRET_KEY=dev-secret-key-not-for-production
)

if not defined CORS_ORIGINS (
    echo 设置默认 CORS...
    set CORS_ORIGINS=http://localhost:5181,http://localhost:3000
)

REM 启动后端
start "shiji-backend" cmd /k "python app.py"
echo 后端已启动！
echo.
echo 提示：首次使用请复制 .env.template 为 .env 并配置实际值
pause
