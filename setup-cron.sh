#!/bin/bash
# 使用 Cron 设置自动数据同步

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cron 定时任务设置脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${YELLOW}脚本目录: ${SCRIPT_DIR}${NC}"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi

PYTHON_PATH=$(which python3)
echo -e "${GREEN}Python 路径: ${PYTHON_PATH}${NC}"

# 检查 getdata.py
if [ ! -f "$SCRIPT_DIR/getdata.py" ]; then
    echo -e "${RED}错误: 未找到 getdata.py 文件${NC}"
    exit 1
fi

# 设置执行时间
read -p "请输入执行时间的小时（0-23，默认 2）: " HOUR
HOUR=${HOUR:-2}

read -p "请输入执行时间的分钟（0-59，默认 0）: " MINUTE
MINUTE=${MINUTE:-0}

# 验证输入
if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
    echo -e "${RED}错误: 小时必须在 0-23 之间${NC}"
    exit 1
fi

if ! [[ "$MINUTE" =~ ^[0-9]+$ ]] || [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
    echo -e "${RED}错误: 分钟必须在 0-59 之间${NC}"
    exit 1
fi

echo -e "${GREEN}执行时间设置为: ${HOUR}:${MINUTE}${NC}"

# 日志文件路径
LOG_FILE="$SCRIPT_DIR/sync.log"

# 创建 cron 任务
CRON_JOB="${MINUTE} ${HOUR} * * * cd ${SCRIPT_DIR} && ${PYTHON_PATH} ${SCRIPT_DIR}/getdata.py >> ${LOG_FILE} 2>&1"

# 检查是否已存在相同的任务
if crontab -l 2>/dev/null | grep -q "getdata.py"; then
    echo -e "${YELLOW}检测到已存在的 cron 任务${NC}"
    read -p "是否要替换现有任务？(y/n): " REPLACE
    if [ "$REPLACE" = "y" ] || [ "$REPLACE" = "Y" ]; then
        # 删除旧任务
        crontab -l 2>/dev/null | grep -v "getdata.py" | crontab -
        echo -e "${YELLOW}已删除旧任务${NC}"
    else
        echo -e "${YELLOW}取消操作${NC}"
        exit 0
    fi
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cron 任务已添加！${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "${YELLOW}当前 cron 任务:${NC}"
crontab -l | grep getdata.py

echo -e "\n${GREEN}常用命令:${NC}"
echo -e "  查看所有任务: ${YELLOW}crontab -l${NC}"
echo -e "  编辑任务: ${YELLOW}crontab -e${NC}"
echo -e "  查看日志: ${YELLOW}tail -f ${LOG_FILE}${NC}"
echo -e "  删除任务: ${YELLOW}crontab -e${NC} (然后删除对应行)"

