@echo off
echo 安装Python依赖包...
pip install -r requirements.txt

echo.
echo 运行数据导入程序...
python dataIn.py

pause



