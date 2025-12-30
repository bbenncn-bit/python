# Ubuntu Server 快速设置指南

## 🚀 快速开始（推荐使用 systemd）

### 方法1：使用自动化脚本（最简单）

```bash
# 1. 上传文件到服务器后，进入项目目录
cd /home/ubuntu/python

# 2. 给脚本添加执行权限
chmod +x install-systemd-service.sh

# 3. 运行安装脚本
./install-systemd-service.sh

# 脚本会提示您：
# - 确认 Python 路径
# - 确认脚本路径
# - 设置执行时间（默认凌晨2:00）
```

### 方法2：手动设置 systemd（推荐）

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/data-sync.service
```

复制以下内容（**修改路径为您的实际路径**）：

```ini
[Unit]
Description=数据同步服务 - 自动同步废钢和报废车数据
After=network.target mysql.service

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/python
ExecStart=/usr/bin/python3 /home/ubuntu/python/getdata.py
StandardOutput=journal
StandardError=journal
Environment="PYTHONUNBUFFERED=1"
TimeoutStartSec=3600
```

```bash
# 2. 创建定时器文件
sudo nano /etc/systemd/system/data-sync.timer
```

复制以下内容：

```ini
[Unit]
Description=数据同步定时器 - 每天凌晨2:00执行
Requires=data-sync.service

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

```bash
# 3. 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable data-sync.timer
sudo systemctl start data-sync.timer

# 4. 检查状态
sudo systemctl status data-sync.timer
```

## 📋 常用命令

```bash
# 查看定时器状态
sudo systemctl status data-sync.timer

# 查看下次执行时间
sudo systemctl list-timers data-sync.timer

# 手动执行一次（测试）
sudo systemctl start data-sync.service

# 查看执行日志
sudo journalctl -u data-sync.service -f

# 查看最近50条日志
sudo journalctl -u data-sync.service -n 50

# 停止定时器
sudo systemctl stop data-sync.timer

# 禁用定时器（取消开机自启）
sudo systemctl disable data-sync.timer
```

## ⚙️ 修改执行时间

编辑定时器文件：

```bash
sudo nano /etc/systemd/system/data-sync.timer
```

修改 `OnCalendar` 行：
- `OnCalendar=*-*-* 02:00:00` - 每天凌晨2:00
- `OnCalendar=*-*-* 03:30:00` - 每天凌晨3:30
- `OnCalendar=*-*-* 01:00:00` - 每天凌晨1:00

然后重新加载：

```bash
sudo systemctl daemon-reload
sudo systemctl restart data-sync.timer
```

## 🔍 故障排查

### 检查 Python 环境

```bash
# 检查 Python 版本
python3 --version

# 检查依赖是否安装
pip3 list | grep -E "pymysql|requests|cryptography"

# 如果缺少依赖，安装
cd /home/ubuntu/python
pip3 install -r requirements.txt
```

### 手动测试脚本

```bash
cd /home/ubuntu/python
python3 getdata.py
```

### 查看详细错误

```bash
# 查看服务日志
sudo journalctl -u data-sync.service -n 100 --no-pager

# 实时查看日志
sudo journalctl -u data-sync.service -f
```

## 📝 使用 Cron 的快速方法

如果您 prefer 使用 cron：

```bash
# 1. 运行自动化脚本
chmod +x setup-cron.sh
./setup-cron.sh

# 或手动编辑
crontab -e

# 2. 添加以下行（修改路径）
0 2 * * * cd /home/ubuntu/python && /usr/bin/python3 /home/ubuntu/python/getdata.py >> /home/ubuntu/python/sync.log 2>&1
```

## ✅ 验证设置

1. **检查定时器是否运行**：
   ```bash
   sudo systemctl status data-sync.timer
   ```

2. **查看下次执行时间**：
   ```bash
   sudo systemctl list-timers data-sync.timer
   ```

3. **手动执行测试**：
   ```bash
   sudo systemctl start data-sync.service
   sudo journalctl -u data-sync.service -f
   ```

4. **等待自动执行后检查日志**：
   ```bash
   sudo journalctl -u data-sync.service --since "1 hour ago"
   ```

## 📚 详细文档

更多详细信息请参考：`ubuntu-auto-sync-setup.md`

