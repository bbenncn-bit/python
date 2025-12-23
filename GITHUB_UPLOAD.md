# GitHub 上传指南

## ⚠️ 重要安全提示

**在上传之前，请注意：**

1. **代码中包含敏感信息**：
   - 数据库密码：`Monica#!wapers0311`
   - API密钥和私钥
   - 数据库服务器地址

2. **建议操作**：
   - 如果这是公开仓库，请先移除或替换所有敏感信息
   - 使用环境变量或配置文件管理敏感信息
   - 如果已上传包含敏感信息的代码，请立即更换所有密钥和密码

## 上传步骤

### 方法1：使用命令行（推荐）

#### 1. 初始化Git仓库

```bash
cd F:\python
git init
```

#### 2. 添加所有文件

```bash
git add .
```

#### 3. 提交文件

```bash
git commit -m "Initial commit: 数据同步工具"
```

#### 4. 添加远程仓库

```bash
git remote add origin https://github.com/bbenncn-bit/python.git
```

#### 5. 推送代码

```bash
git branch -M main
git push -u origin main
```

### 方法2：使用GitHub Desktop

1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 登录你的GitHub账号
3. 点击 "File" -> "Add Local Repository"
4. 选择 `F:\python` 目录
5. 点击 "Publish repository"
6. 选择 `bbenncn-bit/python` 仓库

### 方法3：使用VS Code

1. 在VS Code中打开 `F:\python` 文件夹
2. 点击左侧的源代码管理图标（或按 `Ctrl+Shift+G`）
3. 点击"初始化仓库"
4. 暂存所有更改
5. 输入提交信息并提交
6. 点击"发布分支"或使用命令：
   ```bash
   git remote add origin https://github.com/bbenncn-bit/python.git
   git push -u origin main
   ```

## 如果遇到问题

### 问题1：需要身份验证

如果提示需要登录，可以使用：

1. **Personal Access Token**（推荐）：
   - 在GitHub设置中创建Token
   - 使用Token作为密码

2. **SSH密钥**：
   ```bash
   git remote set-url origin git@github.com:bbenncn-bit/python.git
   ```

### 问题2：仓库已存在内容

如果远程仓库已有内容，需要先拉取：

```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### 问题3：需要强制推送（谨慎使用）

```bash
git push -u origin main --force
```

## 后续更新

上传后，每次更新代码：

```bash
git add .
git commit -m "更新说明"
git push
```

## 忽略的文件

`.gitignore` 文件已配置忽略以下内容：

- Python缓存文件（`__pycache__`）
- 虚拟环境（`venv/`, `env/`）
- IDE配置文件
- 日志文件
- 环境变量文件（`.env`）

## 安全建议

1. **使用环境变量**：
   - 创建 `.env` 文件存储敏感信息
   - 将 `.env` 添加到 `.gitignore`
   - 创建 `.env.example` 作为模板

2. **使用配置文件**：
   - 创建 `config.example.py` 作为模板
   - 实际配置使用 `config.local.py`（已忽略）

3. **定期更换密钥**：
   - 如果代码已公开，立即更换所有密钥
   - 使用GitHub Secrets存储敏感信息（如果使用GitHub Actions）

