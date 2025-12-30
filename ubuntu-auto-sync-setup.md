# Ubuntu Server 自动同步设置指南

本指南将帮助您在 Ubuntu Server 22.04 上设置自动定时任务，每天凌晨自动执行 `getdata.py` 同步数据。

## 前置条件

1. 已安装 Python 3
2. 已安装所有依赖包
3. 脚本可以手动正常运行

## 方案一：使用 systemd Timer（推荐）

systemd timer 是 Ubuntu 系统推荐的定时任务方式，提供更好的日志管理和服务控制。

### 步骤 1：准备脚本目录

假设您的 Python 项目在 `/home/ubuntu/python` 目录下：

```bash
# 确认脚本路径
cd /home/ubuntu/python
ls -la getdata.py

# 确保脚本有执行权限
chmod +x getdata.py
```

### 步骤 2：创建 systemd 服务文件

创建服务文件 `/etc/systemd/system/data-sync.service`：

```bash
sudo nano /etc/systemd/system/data-sync.service
```

将以下内容复制进去（**请根据实际情况修改路径**）：

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

# 环境变量（如果需要）
Environment="PYTHONUNBUFFERED=1"

# 超时设置（可选）
TimeoutStartSec=3600
```

**重要：请修改以下路径为您的实际路径：**
- `User=ubuntu` - 改为您的用户名
- `WorkingDirectory=/home/ubuntu/python` - 改为您的Python项目路径
- `ExecStart=/usr/bin/python3 /home/ubuntu/python/getdata.py` - 改为您的Python和脚本路径

### 步骤 3：创建 systemd Timer 文件

创建定时器文件 `/etc/systemd/system/data-sync.timer`：

```bash
sudo nano /etc/systemd/system/data-sync.timer
```

将以下内容复制进去：

```ini
[Unit]
Description=数据同步定时器 - 每天凌晨2:00执行
Requires=data-sync.service

[Timer]
# 每天凌晨 2:00 执行
OnCalendar=*-*-* 02:00:00
# 如果服务器在定时执行时关机，开机后立即执行一次
Persistent=true
# 随机延迟0-300秒，避免系统负载过高
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

**修改执行时间：**
- `OnCalendar=*-*-* 02:00:00` - 每天凌晨2:00
- 可以改为其他时间，例如：
  - `OnCalendar=*-*-* 03:00:00` - 每天凌晨3:00
  - `OnCalendar=*-*-* 01:30:00` - 每天凌晨1:30

### 步骤 4：重新加载 systemd 并启用服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用定时器（开机自启）
sudo systemctl enable data-sync.timer

# 启动定时器
sudo systemctl start data-sync.timer

# 检查定时器状态
sudo systemctl status data-sync.timer
```

### 步骤 5：验证设置

```bash
# 查看定时器状态
sudo systemctl status data-sync.timer

# 查看下次执行时间
sudo systemctl list-timers data-sync.timer

# 手动测试执行一次（不等待定时器）
sudo systemctl start data-sync.service

# 查看执行日志
sudo journalctl -u data-sync.service -f
```

### 常用管理命令

```bash
# 查看定时器状态
sudo systemctl status data-sync.timer

# 查看所有定时器
sudo systemctl list-timers

# 查看服务日志
sudo journalctl -u data-sync.service -n 50

# 实时查看日志
sudo journalctl -u data-sync.service -f

# 停止定时器
sudo systemctl stop data-sync.timer

# 禁用定时器（取消开机自启）
sudo systemctl disable data-sync.timer

# 重新启动定时器
sudo systemctl restart data-sync.timer
```

## 方案二：使用 Cron（简单直接）

如果 prefer 使用传统的 cron，可以按以下步骤操作。

### 步骤 1：编辑 crontab

```bash
crontab -e
```

### 步骤 2：添加定时任务

在文件末尾添加以下行（**请根据实际情况修改路径**）：

```cron
# 每天凌晨 2:00 执行数据同步
0 2 * * * cd /home/ubuntu/python && /usr/bin/python3 /home/ubuntu/python/getdata.py >> /home/ubuntu/python/sync.log 2>&1
```

**说明：**
- `0 2 * * *` - 每天凌晨2:00执行
- `cd /home/ubuntu/python` - 切换到脚本目录
- `>> /home/ubuntu/python/sync.log 2>&1` - 将输出和错误保存到日志文件

**修改执行时间：**
- `0 3 * * *` - 每天凌晨3:00
- `30 1 * * *` - 每天凌晨1:30
- `0 */6 * * *` - 每6小时执行一次

### 步骤 3：验证 crontab

```bash
# 查看当前的 crontab
crontab -l

# 查看 cron 服务状态
sudo systemctl status cron
```

### 步骤 4：测试执行

```bash
# 手动执行一次测试
cd /home/ubuntu/python
python3 getdata.py

# 查看日志
tail -f /home/ubuntu/python/sync.log
```

## 方案对比

| 特性 | systemd Timer | Cron |
|------|---------------|------|
| 日志管理 | 集成到 systemd journal | 需要手动配置日志文件 |
| 服务管理 | 完整的 systemd 工具 | 基本的 cron 工具 |
| 开机自启 | 自动支持 | 需要确保 cron 服务运行 |
| 错误处理 | 更好的错误报告 | 需要手动处理 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 故障排查

### 问题1：脚本无法执行

```bash
# 检查 Python 路径
which python3

# 检查脚本权限
ls -la /home/ubuntu/python/getdata.py

# 手动执行测试
cd /home/ubuntu/python
python3 getdata.py
```

### 问题2：找不到 Python 模块

```bash
# 检查 Python 环境
python3 -m pip list

# 安装依赖
cd /home/ubuntu/python
pip3 install -r requirements.txt
```

### 问题3：数据库连接失败

- 检查数据库服务器是否可访问
- 检查防火墙设置
- 检查数据库用户权限

### 问题4：查看详细日志

**systemd 方式：**
```bash
sudo journalctl -u data-sync.service -n 100 --no-pager
```

**cron 方式：**
```bash
tail -n 100 /home/ubuntu/python/sync.log
```

## 安全建议

1. **不要将敏感信息硬编码在脚本中**
   - 考虑使用环境变量或配置文件
   - 将配置文件权限设置为 600

2. **定期检查日志**
   ```bash
   # 每天检查一次日志
   sudo journalctl -u data-sync.service --since "24 hours ago"
   ```

3. **监控任务执行**
   - 设置邮件通知（如果任务失败）
   - 或使用监控工具

## 下一步

设置完成后，建议：

1. 等待第一次自动执行
2. 检查日志确认执行成功
3. 验证数据库中的数据是否更新
4. 设置日志轮转（避免日志文件过大）

## 日志轮转设置（可选）

创建日志轮转配置 `/etc/logrotate.d/data-sync`：

```bash
sudo nano /etc/logrotate.d/data-sync
```

内容：
```
/home/ubuntu/python/sync.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
}
```

