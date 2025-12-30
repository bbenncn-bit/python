# Excel数据导入MySQL工具

这个工具用于将Excel文件中的数据结构和数据批量导入到MySQL数据库中。

## 功能特点

- 自动读取Excel文件中的"数据结构"sheet，创建对应的MySQL表结构
- 自动读取Excel文件中的"具体数值"sheet，将数据导入到MySQL表中
- 支持批量处理多个Excel文件
- 自动映射Excel数据类型到MySQL数据类型
- 支持中文注释和字段名

## 文件说明

- `dataIn.py` - 处理单个Excel文件（energyAnalysisStrategy.xlsx）
- `dataIn_batch.py` - 批量处理data文件夹中的所有Excel文件
- `requirements.txt` - Python依赖包列表
- `run.bat` - Windows批处理脚本，用于安装依赖并运行程序

## 安装依赖

### 方法1：使用稳定版本（推荐）

```bash
install_stable.bat
```

或者手动安装：

```bash
pip install -r requirements_stable.txt
```

### 方法2：使用最新版本

```bash
pip install -r requirements.txt
```

### 如果遇到numpy/pandas版本冲突错误

运行修复脚本：

```bash
fix_dependencies.bat
```

## 程序优化说明

### 最新修复内容

1. **智能列名识别**：程序现在能自动识别Excel中的列名（字段、类型、中文含义等）
2. **正确的数据类型映射**：
   - "整数" → INT
   - "字符串" → VARCHAR(255)
   - "对象" → JSON
   - "数值" → DECIMAL(10,2)
3. **修复数据库连接**：解决了密码中特殊字符导致的连接问题
4. **增强数据导入**：提供多种数据导入方式，确保数据能成功导入
5. **详细调试信息**：显示更多处理过程信息，便于排查问题

### 测试程序功能

运行测试脚本验证环境：

```bash
python test_connection.py
```

## 常见问题解决

### 错误：numpy.dtype size changed

这是numpy和pandas版本不兼容导致的，解决方法：

1. 卸载现有包：
```bash
pip uninstall pandas numpy sqlalchemy pymysql openpyxl -y
```

2. 安装稳定版本：
```bash
pip install -r requirements_stable.txt
```

### 错误：Can't connect to MySQL server

1. 检查网络连接
2. 确认数据库服务器地址和端口
3. 验证用户名和密码
4. 运行测试脚本：`python test_connection.py`

## 使用方法

### 方法1：处理单个文件

```bash
python dataIn.py
```

这将处理 `data/energyAnalysisStrategy.xlsx` 文件，创建 `energyAnalysisStrategy` 表。

### 方法2：批量处理所有文件

```bash
python dataIn_batch.py
```

这将处理 `data/` 文件夹中的所有 `.xlsx` 文件。

## Excel文件格式要求

每个Excel文件需要包含两个sheet：

1. **数据结构** sheet - 定义表结构
   - 第一列：字段名
   - 第二列：数据类型
   - 第三列：字段注释（可选）

2. **具体数值** sheet - 包含实际数据
   - 列名应与"数据结构"sheet中的字段名对应

## 支持的数据类型

程序会自动将以下Excel数据类型映射为MySQL数据类型：

- varchar → VARCHAR(255)
- text → TEXT
- int/integer → INT
- bigint → BIGINT
- float → FLOAT
- double → DOUBLE
- decimal → DECIMAL(10,2)
- date → DATE
- datetime → DATETIME
- timestamp → TIMESTAMP
- boolean/bool → BOOLEAN

## 数据库配置

程序默认连接到以下MySQL数据库：

- 服务器：124.223.182.79
- 端口：3306
- 用户名：root
- 密码：Monica#!wapers0311
- 数据库：pls

如需修改数据库配置，请编辑程序中的 `DB_CONFIG` 字典。

## 注意事项

1. 确保MySQL数据库服务正在运行
2. 确保网络可以访问远程MySQL服务器
3. 确保有足够的权限创建表和插入数据
4. 如果表已存在，程序会追加数据而不是覆盖
5. 程序会自动处理中文字符编码

## 错误处理

程序包含完整的错误处理机制：

- 数据库连接失败时会显示错误信息
- Excel文件读取失败时会跳过该文件
- 表创建失败时会显示具体错误
- 数据导入失败时会显示错误信息

## 输出信息

程序运行时会显示详细的处理信息：

- 数据库连接状态
- Excel文件读取状态
- 表创建SQL语句
- 数据导入进度
- 处理结果统计
