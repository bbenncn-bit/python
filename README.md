# 数据同步工具

自动从API获取废钢和报废车数据，并同步到MySQL数据库。

## ⚠️ 安全提示

**重要：** 本仓库包含敏感信息（API密钥、数据库密码等）。上传到GitHub前，请确保：

1. 使用环境变量或配置文件管理敏感信息
2. 不要将包含真实密码的代码提交到公开仓库
3. 如果已提交，请立即更换所有密钥和密码

## 功能特点

- 🔄 自动同步废钢和报废车数据
- 📊 智能数据增量更新（只同步缺失的数据）
- 🔐 RSA数字签名认证
- 🗄️ 自动创建和更新数据库表结构
- 📝 详细的日志输出

## 项目结构

```
python/
├── getdata.py              # 主数据同步脚本
├── rsg.py                  # 总部数据同步工具
├── dataIn.py              # Excel数据导入工具（单文件）
├── dataIn_batch.py        # Excel数据导入工具（批量）
├── test_connection.py      # 数据库连接测试
├── verify_data.py         # 数据验证工具
├── requirements.txt       # Python依赖包
├── requirements_stable.txt # 稳定版本依赖
└── data/                  # Excel数据文件目录
```

## 安装依赖

### 方法1：使用稳定版本（推荐）

```bash
install_stable.bat
```

或手动安装：

```bash
pip install -r requirements_stable.txt
```

### 方法2：使用最新版本

```bash
pip install -r requirements.txt
```

### 如果遇到依赖冲突

运行修复脚本：

```bash
fix_dependencies.bat
```

## 使用方法

### 数据同步（自动）

```bash
python getdata.py
```

程序会自动：
1. 获取API token
2. 检查数据库中的最新数据日期
3. 从最新日期开始同步到当前日期
4. 自动创建和更新表结构

### Excel数据导入

#### 单文件导入

```bash
python dataIn.py
```

#### 批量导入

```bash
python dataIn_batch.py
```

### 测试数据库连接

```bash
python test_connection.py
```

## 配置说明

### API配置

在 `getdata.py` 中配置：

```python
APP_ID = "your_app_id"
ACCESS_KEY = "your_access_key"
PRIVATE_KEY = """your_private_key"""
```

### 数据库配置

在脚本中配置数据库连接信息：

```python
conn = pymysql.connect(
    host='your_host',
    port=3306,
    user='your_user',
    password='your_password',
    database='your_database',
    charset='utf8mb4'
)
```

## 数据表

- `receiptfg` - 废钢数据表
- `receiptfc` - 报废车数据表

## 注意事项

1. ⚠️ **安全警告**：代码中包含敏感信息，请勿直接提交到公开仓库
2. 确保MySQL数据库服务正在运行
3. 确保网络可以访问API和数据库服务器
4. 程序会自动处理表结构创建和字段更新
5. 支持增量同步，不会重复插入已有数据

## 错误处理

程序包含完整的错误处理机制：

- API请求失败时会显示错误信息
- 数据库连接失败时会显示错误信息
- 数据插入失败时会跳过该记录并继续
- 所有错误都会记录到控制台输出

## 日志输出

程序运行时会显示：

- 同步开始和结束时间
- 数据获取进度
- 数据插入统计
- 错误和警告信息

## 许可证

本项目仅供内部使用。

## 贡献

如有问题或建议，请提交Issue或Pull Request。
