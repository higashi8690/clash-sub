@echo off
REM 切换到脚本所在目录
cd /d %~dp0

REM 执行 Ryia_auto.py 并等待完成
echo 正在执行 Ryia_auto.py，请耐心等待...
python Ryia_auto.py
if errorlevel 1 (
    echo Ryia_auto.py 执行失败
    pause
    exit /b 1
)

REM 确保 Ryia_auto.py 完全执行完后再执行 add_group.py
echo 正在执行 add_group.py...
python add_group.py
if errorlevel 1 (
    echo add_group.py 执行失败
    pause
    exit /b 1
)

echo 所有脚本执行完成
pause