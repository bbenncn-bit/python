#!/bin/bash
# 自动安装 systemd 服务脚本
# 用于在 Ubuntu Server 上设置自动数据同步

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}数据同步服务安装脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取当前用户
CURRENT_USER=$(whoami)
echo -e "${YELLOW}当前用户: ${CURRENT_USER}${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${YELLOW}脚本目录: ${SCRIPT_DIR}${NC}"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3${NC}"
    exit 1
fi

PYTHON_PATH=$(which python3)
echo -e "${GREEN}Python 路径: ${PYTHON_PATH}${NC}"

# 检查 getdata.py
if [ ! -f "$SCRIPT_DIR/getdata.py" ]; then
    echo -e "${RED}错误: 未找到 getdata.py 文件${NC}"
    exit 1
fi

echo -e "${GREEN}找到 getdata.py: $SCRIPT_DIR/getdata.py${NC}"

# 设置执行时间（默认凌晨2:00）
read -p "请输入执行时间（格式：HH:MM，默认 02:00）: " EXEC_TIME
EXEC_TIME=${EXEC_TIME:-02:00}

# 验证时间格式
if ! [[ $EXEC_TIME =~ ^([0-1][0-9]|2[0-3]):[0-5][0-9]$ ]]; then
    echo -e "${RED}错误: 时间格式不正确，请使用 HH:MM 格式${NC}"
    exit 1
fi

HOUR=$(echo $EXEC_TIME | cut -d: -f1)
MINUTE=$(echo $EXEC_TIME | cut -d: -f2)

echo -e "${GREEN}执行时间设置为: ${HOUR}:${MINUTE}${NC}"

# 创建服务文件
echo -e "${YELLOW}创建 systemd 服务文件...${NC}"
sudo tee /etc/systemd/system/data-sync.service > /dev/null <<EOF
[Unit]
Description=数据同步服务 - 自动同步废钢和报废车数据
After=network.target mysql.service

[Service]
Type=oneshot
User=${CURRENT_USER}
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${PYTHON_PATH} ${SCRIPT_DIR}/getdata.py
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"
TimeoutStartSec=3600

[Install]
WantedBy=multi-user.target
EOF

# 创建定时器文件
echo -e "${YELLOW}创建 systemd 定时器文件...${NC}"
sudo tee /etc/systemd/system/data-sync.timer > /dev/null <<EOF
[Unit]
Description=数据同步定时器 - 每天 ${EXEC_TIME} 执行
Requires=data-sync.service

[Timer]
OnCalendar=*-*-* ${HOUR}:${MINUTE}:00
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

# 重新加载 systemd
echo -e "${YELLOW}重新加载 systemd 配置...${NC}"
sudo systemctl daemon-reload

# 启用并启动定时器
echo -e "${YELLOW}启用定时器...${NC}"
sudo systemctl enable data-sync.timer
sudo systemctl start data-sync.timer

# 检查状态
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "${YELLOW}定时器状态:${NC}"
sudo systemctl status data-sync.timer --no-pager -l

echo -e "\n${YELLOW}下次执行时间:${NC}"
sudo systemctl list-timers data-sync.timer --no-pager

echo -e "\n${GREEN}常用命令:${NC}"
echo -e "  查看状态: ${YELLOW}sudo systemctl status data-sync.timer${NC}"
echo -e "  查看日志: ${YELLOW}sudo journalctl -u data-sync.service -f${NC}"
echo -e "  手动执行: ${YELLOW}sudo systemctl start data-sync.service${NC}"
echo -e "  停止定时器: ${YELLOW}sudo systemctl stop data-sync.timer${NC}"

