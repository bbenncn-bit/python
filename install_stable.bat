@echo off
echo 安装稳定版本的Python依赖包...

echo.
echo 卸载现有版本...
pip uninstall pandas numpy sqlalchemy pymysql openpyxl -y

echo.
echo 安装稳定版本...
pip install -r requirements_stable.txt

echo.
echo 验证安装...
python -c "import pandas; import numpy; import pymysql; import sqlalchemy; print('✓ 所有包安装成功！')"

if %errorlevel% equ 0 (
    echo.
    echo 安装完成！现在可以运行程序了。
    echo 运行命令: python dataIn.py
) else (
    echo.
    echo 安装失败，请检查Python环境。
)

pause



