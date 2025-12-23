@echo off
echo 正在修复Python包版本冲突...

echo.
echo 卸载可能冲突的包...
pip uninstall pandas numpy sqlalchemy -y

echo.
echo 安装兼容的版本...
pip install numpy==1.24.3
pip install pandas==1.5.3
pip install openpyxl==3.1.2
pip install pymysql==1.1.0
pip install sqlalchemy==1.4.50

echo.
echo 验证安装...
python -c "import pandas; import numpy; import pymysql; import sqlalchemy; print('所有包安装成功！')"

echo.
echo 现在可以运行程序了...
python dataIn.py

pause



