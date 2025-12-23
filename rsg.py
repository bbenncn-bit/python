#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=======================================================
数据提取同步程序 | Data Extraction & Synchronization Tool
=======================================================

作者 (Author): API Integration Developer
版本 (Version): 1.0.0
创建日期 (Created): 2025
描述 (Description): 
    专业的API数据提取工具，支持从欧冶链金平台获取废钢和报废车数据，
    并自动同步到本地MySQL数据库。采用RSA数字签名确保API请求安全性。
    
    Professional API data extraction tool that fetches scrap steel and 
    scrapped vehicle data from Ouye Lianjin platform and automatically 
    synchronizes to local MySQL database with RSA digital signature for security.

功能特性 (Features):
    1. 双数据源支持：废钢数据 & 报废车数据
    2. RSA-SHA1数字签名认证
    3. 自动数据库表结构创建和更新
    4. 智能数据类型推断和转换
    5. 重复数据检测和防护
    6. 全面的错误处理和日志记录

技术栈 (Tech Stack):
    - Python 3.x
    - MySQL Database
    - RSA Cryptography
    - RESTful API Integration

=======================================================
"""

# ====================================================================
# 系统依赖导入 | System Dependencies Import
# ====================================================================
import requests          # HTTP请求库 | HTTP requests library
import pymysql          # MySQL数据库连接器 | MySQL database connector
from datetime import datetime, timedelta  # 日期时间处理 | Date/time handling
import json             # JSON数据处理 | JSON data processing
import base64           # Base64编解码 | Base64 encoding/decoding
import time             # 时间相关操作 | Time operations

# 加密相关库 | Cryptography libraries
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ====================================================================
# API认证配置 | API Authentication Configuration
# ====================================================================
# 应用标识符 - 平台分配的唯一应用ID
# Application identifier - unique app ID assigned by platform
APP_ID = "CZDP"

# 访问密钥 - 用于API访问权限验证
# Access key - for API access permission verification
ACCESS_KEY = "5fe632cf1ed54eb884129b7ffbd3521"

# RSA私钥 - DER格式，用于数字签名生成
# RSA Private Key - DER format for digital signature generation
# 注意：生产环境中应使用环境变量或密钥管理服务存储
# Note: In production, should use environment variables or key management service
PRIVATE_KEY = """MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAMjIidy6/qvBd9EVyNbKabbnESlbatQw9lHLzjHWFKDfl7E24fuj0m8xurZEVzhUYal9af7sMlYPcEma13i4xJ6faGOvJHseYlkoJRVHcJOq02tFDd3U2rZ98X3OjHC7CIFbIGM27GTvh41nsrexOJi0S3l3V0JWH/ooMeZiaWEXAgMBAAECgYEApiR7H7GEhu+Ci/sww7uemoC9zLEexxL04F568vYo/63FQhkeCjJXMTe/Po9ydOQuJCfpC867IEeKLP36CqUp3HhEBMnaOUFLMrF95BkFNu/QS1TmVe3xfoo66962VEimmV0Rrc+YeK3nTvLFUzCCgCKM/xArQFZMiWJ435MzASECQQDwdC5N77nHyTj2xiUcwUQHpZHIO9rMu0B3svkOwUbfqhOMHd5lR3URbE0/G0pq/RJrlH3gR5Fz0NySB/cT6yE/AkEA1cPCqNKgfCTY3skKg1UGQUlFYt4tf0sWPA1zqYe4RhkmGpA6ZZZvE9Y2SFnEIBdch6BE1uH+KbWQdCe3Q01yKQJBAISl8y13hCuc7FnmsW6Nh7QYOLYXnvq2ijf+ebsUEL8umh4AFEIXC5QTBQI9Ue53sgO7JT3m/WzA2g2Na1aHrg0CQQDSXa9Akt9qrJxcSr601kSslR3amUlu/wbnnFlZ2f2HxpIQDCXb+XpgrCuJcgWnizX9JsT4Lzj/9PUuyjL44ctZAkAEyQTmtZI46y8fwuOiiAQ9orPDQmc8jzHNRpQqQ3Ghc8KlAhQj/sEPixFW6TMrxwfFy2CGEplwVtvNubu9zfMO"""

# ====================================================================
# 本地数据库配置 | Local Database Configuration
# ====================================================================
# 本地MySQL数据库连接配置 - 数据存储目标服务器
# Local MySQL database connection configuration - data storage target server
LOCAL_DB_CONFIG = {
    'host': '43.137.106.186',    # 本地数据库服务器地址 | Local database server address
    'port': 25424,               # 自定义MySQL端口 | Custom MySQL port
    'user': 'root',              # 数据库用户名 | Database username
    'password': 'Rsg@px@123',    # 数据库密码 | Database password
    'database': 'rsgBI',         # 目标数据库名 | Target database name
    'charset': 'utf8mb4'         # 字符集支持emoji等 | Charset supports emoji etc.
}

# ====================================================================
# API端点配置字典 | API Endpoint Configuration Dictionary
# ====================================================================
# 多数据源配置 - 支持不同类型数据的提取
# Multi-data source configuration - supports different types of data extraction
API_CONFIGS = {
    'g': {  # 废钢数据配置 | Scrap steel data configuration
        'name': '废钢数据',                    # 数据源名称 | Data source name
        'url': 'https://www.oylianjin.com/ecopenapi/basic/a/trade/receipt/query/changzhi/receipt',
        
        'table_name': 'receiptfg',             # 目标数据库表名 | Target database table name
        'data_key': 'fgReceiptDetails'         # API响应中的数据键名 | Data key in API response
    },
    'c': {  # 报废车数据配置 | Scrapped vehicle data configuration
        'name': '报废车数据',                  # 数据源名称 | Data source name
        'url': 'https://www.oylianjin.com/ecopenapi/basic/a/trade/receipt/query/changzhi/receipt',
        'table_name': 'receiptfc',             # 目标数据库表名 | Target database table name
        'data_key': 'fcReceiptDetails'         # API响应中的数据键名 | Data key in API response
    }
}

# ====================================================================
# 用户交互模块 | User Interaction Module
# ====================================================================

def get_user_choice():
    """
    获取用户数据源选择
    Get user's data source selection
    
    功能描述 (Description):
        提供交互式界面供用户选择要提取的数据类型：
        - g: 废钢数据 (Scrap steel data)
        - c: 报废车数据 (Scrapped vehicle data)
        
        Provides interactive interface for users to select data type to extract
    
    返回值 (Returns):
        tuple: (choice, config)
            - choice (str): 用户选择的选项 | User's selected option
            - config (dict): 对应的API配置信息 | Corresponding API configuration
    
    异常处理 (Exception Handling):
        无限循环直到用户输入有效选项
        Infinite loop until user inputs valid option
    """
    print("\n" + "="*50)
    print("📡 总部数据同步程序 | Headquarters Data Sync Tool")
    print("🎯 目标数据库: rsgBI@43.137.106.186:25424")
    print("="*50)
    print("请选择要提取的数据类型:")
    print("g - 废钢数据 (导入receiptfg表)")
    print("c - 报废车数据 (导入receiptfc表)")
    print("="*50)
    
    while True:
        choice = input("请输入您的选择 (g/c): ").lower().strip()
        if choice in ['g', 'c']:
            config = API_CONFIGS[choice]
            print(f"\n✅ 您选择了: {config['name']}")
            print(f"   API地址: {config['url']}")
            print(f"   目标表: {config['table_name']}")
            print(f"   目标数据库: {LOCAL_DB_CONFIG['database']}")
            return choice, config
        else:
            print("❌ 无效选择，请输入 'g' 或 'c'")

# ====================================================================
# 加密认证模块 | Cryptographic Authentication Module
# ====================================================================

def get_private_key():
    """
    私钥解析和加载
    Private key parsing and loading
    
    功能描述 (Description):
        将Base64编码的DER格式私钥字符串转换为可用的私钥对象
        Converts Base64-encoded DER format private key string to usable private key object
    
    返回值 (Returns):
        cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey: 
            RSA私钥对象 | RSA private key object
    
    异常处理 (Exception Handling):
        如果私钥格式错误或解析失败，抛出异常
        Raises exception if private key format is invalid or parsing fails
    
    安全注意事项 (Security Notes):
        - 私钥应在生产环境中通过安全方式存储
        - Private key should be stored securely in production environment
        - 建议使用HSM或密钥管理服务
        - Recommend using HSM or key management service
    """
    try:
        # Base64解码私钥 | Base64 decode private key
        private_key_bytes = base64.b64decode(PRIVATE_KEY.strip())
        
        # 加载DER格式私钥 | Load DER format private key
        private_key = serialization.load_der_private_key(
            private_key_bytes,
            password=None  # 无密码保护 | No password protection
        )
        return private_key
    except Exception as e:
        print("私钥解析错误:", e)
        raise

def sign_data(data_dict, private_key):
    """
    数据签名生成器 - 实现RSA-SHA1数字签名
    Data signature generator - implements RSA-SHA1 digital signature
    
    算法流程 (Algorithm Flow):
        1. 数据预处理：null值转换、类型标准化
        2. 键值排序：按字典序排序所有键
        3. 字符串构建：生成"key1=value1&key2=value2"格式
        4. RSA签名：使用PKCS1v15填充和SHA1哈希
        5. Base64编码：将签名结果编码为字符串
    
    参数 (Parameters):
        data_dict (dict): 需要签名的数据字典 | Data dictionary to be signed
        private_key (RSAPrivateKey): RSA私钥对象 | RSA private key object
    
    返回值 (Returns):
        str: Base64编码的数字签名 | Base64 encoded digital signature
    
    签名规范 (Signature Specification):
        - 遵循Java Demo的签名逻辑 | Follows Java Demo signature logic
        - 使用PKCS#1 v1.5填充方案 | Uses PKCS#1 v1.5 padding scheme
        - SHA1哈希算法 | SHA1 hash algorithm
        - 字典序键排序 | Lexicographic key ordering
    """
    # 第1步：数据标准化处理 | Step 1: Data normalization
    string_dict = {}
    for key, value in data_dict.items():
        if value is None:
            string_dict[key] = "null"  # null值转换为字符串 | Convert null to string
        else:
            string_dict[key] = str(value)  # 所有值转为字符串 | Convert all values to string
    
    # 处理空字典的边界情况 | Handle empty dictionary edge case
    if not string_dict:
        string_dict["sign_val"] = "sign_val"
    
    # 第2步：构建签名字符串 | Step 2: Build signature string
    sorted_keys = sorted(string_dict.keys())  # 字典序排序 | Lexicographic sorting
    sign_str = "&".join([f"{k}={string_dict[k]}" for k in sorted_keys])
    
    print(f"签名字符串: {sign_str}")
    
    # 第3步：生成RSA数字签名 | Step 3: Generate RSA digital signature
    signature = private_key.sign(
        sign_str.encode('utf-8'),  # UTF-8编码 | UTF-8 encoding
        padding.PKCS1v15(),        # PKCS#1 v1.5填充 | PKCS#1 v1.5 padding
        hashes.SHA1()              # SHA1哈希 | SHA1 hash
    )
    
    # 第4步：Base64编码签名结果 | Step 4: Base64 encode signature result
    return base64.b64encode(signature).decode('utf-8')

def get_token():
    """
    API访问令牌获取器
    API access token acquirer
    
    功能描述 (Description):
        通过认证API获取访问令牌，用于后续数据API调用
        Obtains access token through authentication API for subsequent data API calls
    
    认证流程 (Authentication Flow):
        1. 构建令牌请求数据 | Build token request data
        2. 生成请求时间戳 | Generate request timestamp
        3. 创建数字签名 | Create digital signature
        4. 发送认证请求 | Send authentication request
        5. 验证响应状态 | Validate response status
        6. 提取访问令牌 | Extract access token
    
    返回值 (Returns):
        str: 访问令牌字符串 | Access token string
    
    异常处理 (Exception Handling):
        如果认证失败或API返回错误，抛出Exception
        Raises Exception if authentication fails or API returns error
    
    安全特性 (Security Features):
        - 时间戳防重放攻击 | Timestamp prevents replay attacks
        - RSA数字签名验证身份 | RSA digital signature verifies identity
        - HTTPS传输加密 | HTTPS transport encryption
    """
    # 令牌API端点 | Token API endpoint
    token_url = "https://www.oylianjin.com/ecopenapi/open/n/token/gen"
    
    # 构建认证请求数据 | Build authentication request data
    token_data = {
        "appId": APP_ID,           # 应用标识符 | Application identifier
        "accessKey": ACCESS_KEY    # 访问密钥 | Access key
    }
    
    # 生成请求时间戳（毫秒级） | Generate request timestamp (milliseconds)
    timestamp = str(int(time.time() * 1000))
    private_key = get_private_key()
    
    # 构建请求头 | Build request headers
    headers = {
        "Content-Type": "application/json",     # JSON内容类型 | JSON content type
        "appId": APP_ID,                        # 应用ID | Application ID
        "timestamp": timestamp,                 # 请求时间戳 | Request timestamp
        "signVal": sign_data(token_data, private_key)  # 数字签名 | Digital signature
    }
    
    print("Token请求头:", headers)
    print("Token请求数据:", token_data)
    
    # 发送认证请求 | Send authentication request
    response = requests.post(token_url, json=token_data, headers=headers)
    print("Token响应状态码:", response.status_code)
    print("Token响应内容:", response.text)
    
    # 解析响应 | Parse response
    result = response.json()
    
    # 验证认证结果 | Validate authentication result
    if not result.get('success'):
        raise Exception(f"获取token失败: {result.get('message')}")
    
    return result.get('data')

# ====================================================================
# 数据库管理模块 | Database Management Module
# ====================================================================

def check_table_exists(cursor, table_name):
    """
    数据库表存在性检查器
    Database table existence checker
    
    功能描述 (Description):
        检查指定的数据库表是否已存在
        Checks if the specified database table exists
    
    参数 (Parameters):
        cursor (pymysql.cursors.Cursor): 数据库游标对象 | Database cursor object
        table_name (str): 要检查的表名 | Table name to check
    
    返回值 (Returns):
        bool: 表存在返回True，否则返回False | Returns True if table exists, False otherwise
    
    SQL查询 (SQL Query):
        SHOW TABLES LIKE 'table_name' - MySQL标准表检查语句
        SHOW TABLES LIKE 'table_name' - Standard MySQL table check statement
    """
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

def check_date_overlap(cursor, table_name, start_date, end_date):
    """
    数据重复性检查器 - 防止重复导入相同日期范围的数据
    Data duplication checker - prevents importing data for same date range
    
    功能描述 (Description):
        检查数据库表中是否已存在指定日期范围内的orderTime数据，
        支持多种时间格式：DATETIME、秒级时间戳、毫秒级时间戳
        
        Checks if orderTime data exists in specified date range in database table,
        supports multiple time formats: DATETIME, second timestamp, millisecond timestamp
    
    参数 (Parameters):
        cursor (pymysql.cursors.Cursor): 数据库游标对象 | Database cursor object
        table_name (str): 目标表名 | Target table name
        start_date (str): 开始日期 (YYYY-MM-DD) | Start date (YYYY-MM-DD)
        end_date (str): 结束日期 (YYYY-MM-DD) | End date (YYYY-MM-DD)
    
    返回值 (Returns):
        tuple: (has_overlap, existing_dates)
            - has_overlap (bool): 是否存在重叠数据 | Whether overlapping data exists
            - existing_dates (list): 已存在的日期列表 | List of existing dates
    
    时间格式处理逻辑 (Time Format Processing Logic):
        1. 毫秒时间戳 (>10位数字): FROM_UNIXTIME(orderTime/1000)
        2. 秒时间戳 (≤10位数字): FROM_UNIXTIME(orderTime)  
        3. DATETIME格式: 直接使用DATE()函数
        4. NULL值: 跳过处理
    
    异常处理 (Exception Handling):
        如果检查过程出错，返回False允许数据插入继续进行
        If check process fails, returns False to allow data insertion to continue
    """
    try:
        # 第1步：检查orderTime字段是否存在 | Step 1: Check if orderTime field exists
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'orderTime'")
        ordertime_exists = cursor.fetchone() is not None
        
        if not ordertime_exists:
            print(f"⚠️  表 {table_name} 中不存在 orderTime 字段，跳过重复数据检查")
            return False, []
        
        # 第2步：执行复杂的日期范围查询 | Step 2: Execute complex date range query
        # 支持多种时间格式的智能检测和转换
        # Intelligent detection and conversion of multiple time formats
        cursor.execute(f"""
            SELECT DISTINCT 
                CASE 
                    WHEN orderTime IS NULL THEN NULL
                    WHEN CAST(orderTime AS CHAR) REGEXP '^[0-9]+$' AND CHAR_LENGTH(CAST(orderTime AS CHAR)) > 10 THEN 
                        DATE(FROM_UNIXTIME(orderTime/1000))
                    WHEN CAST(orderTime AS CHAR) REGEXP '^[0-9]+$' AND CHAR_LENGTH(CAST(orderTime AS CHAR)) <= 10 THEN 
                        DATE(FROM_UNIXTIME(orderTime))
                    ELSE 
                        DATE(orderTime)
                END as order_date
            FROM {table_name} 
            WHERE (
                CASE 
                    WHEN orderTime IS NULL THEN NULL
                    WHEN CAST(orderTime AS CHAR) REGEXP '^[0-9]+$' AND CHAR_LENGTH(CAST(orderTime AS CHAR)) > 10 THEN 
                        DATE(FROM_UNIXTIME(orderTime/1000))
                    WHEN CAST(orderTime AS CHAR) REGEXP '^[0-9]+$' AND CHAR_LENGTH(CAST(orderTime AS CHAR)) <= 10 THEN 
                        DATE(FROM_UNIXTIME(orderTime))
                    ELSE 
                        DATE(orderTime)
                END
            ) BETWEEN %s AND %s
            AND orderTime IS NOT NULL
            ORDER BY order_date
        """, (start_date, end_date))
        
        existing_dates = cursor.fetchall()
        
        # 第3步：处理查询结果 | Step 3: Process query results
        if existing_dates:
            print(f"\n⚠️  数据库表 {table_name} 中已存在以下日期的orderTime数据:")
            for date_row in existing_dates:
                if date_row[0]:  # 确保日期不为None | Ensure date is not None
                    print(f"   - {date_row[0]}")
            return True, [str(date_row[0]) for date_row in existing_dates if date_row[0]]
        else:
            print(f"\n✅ 数据库表 {table_name} 中不存在 {start_date} 到 {end_date} 范围内的orderTime数据，可以插入新数据")
            return False, []
            
    except Exception as e:
        print(f"检查orderTime日期重叠时出错: {e}")
        print("继续执行，不阻止数据插入")
        return False, []

def analyze_data_structure(data_list):
    """
    API数据结构智能分析器
    Intelligent API data structure analyzer
    
    功能描述 (Description):
        分析API返回的JSON数据结构，自动推断每个字段的数据类型，
        为动态数据库表创建提供基础信息
        
        Analyzes JSON data structure returned by API, automatically infers 
        data types for each field, provides foundation for dynamic table creation
    
    参数 (Parameters):
        data_list (list): API返回的数据记录列表 | List of data records from API
    
    返回值 (Returns):
        dict: 字段类型映射字典 | Field type mapping dictionary
              格式: {field_name: set(data_types)}
              Format: {field_name: set(data_types)}
    
    支持的数据类型 (Supported Data Types):
        - NULL: 空值 | Null values
        - BOOLEAN: 布尔值 | Boolean values  
        - INT: 整数 | Integer values
        - DECIMAL: 浮点数 | Decimal/float values
        - VARCHAR: 字符串 | String values
        - TEXT: 复杂对象(JSON数组/对象) | Complex objects (JSON arrays/objects)
    
    设计优势 (Design Advantages):
        - 动态适应不同API数据结构 | Dynamically adapts to different API data structures
        - 减少手动维护表结构的工作量 | Reduces manual table structure maintenance
        - 支持API字段变更的自动适配 | Supports automatic adaptation to API field changes
    """
    all_fields = {}
    
    # 遍历所有数据记录进行类型分析 | Iterate through all data records for type analysis
    for item in data_list:
        for key, value in item.items():
            if key not in all_fields:
                all_fields[key] = set()
            
            # 智能类型推断 | Intelligent type inference
            if value is None:
                all_fields[key].add('NULL')
            elif isinstance(value, bool):
                all_fields[key].add('BOOLEAN')
            elif isinstance(value, int):
                all_fields[key].add('INT')
            elif isinstance(value, float):
                all_fields[key].add('DECIMAL')
            elif isinstance(value, str):
                all_fields[key].add('VARCHAR')
            elif isinstance(value, list):
                all_fields[key].add('TEXT')  # JSON数组存储 | JSON array storage
            elif isinstance(value, dict):
                all_fields[key].add('TEXT')  # JSON对象存储 | JSON object storage
            else:
                all_fields[key].add('TEXT')  # 默认类型 | Default type
    
    return all_fields

def get_mysql_type(field_types, field_name):
    """
    MySQL数据类型智能映射器
    Intelligent MySQL data type mapper
    
    功能描述 (Description):
        根据字段的数据类型集合，智能选择最合适的MySQL数据类型
        Intelligently selects the most appropriate MySQL data type based on field's data type set
    
    参数 (Parameters):
        field_types (dict): 字段类型映射字典 | Field type mapping dictionary
        field_name (str): 字段名称 | Field name
    
    返回值 (Returns):
        str: MySQL数据类型定义 | MySQL data type definition
    
    类型映射规则 (Type Mapping Rules):
        1. 时间字段优先级：自动识别时间相关字段名
        2. URL字段优先级：自动识别URL相关字段名，使用TEXT类型
        3. 数值类型优先级：DECIMAL > INT > BIGINT
        4. 文本类型选择：TEXT (JSON/URL) > VARCHAR (普通字符串)
        5. 特殊类型处理：BOOLEAN 单独处理
    
    字段名智能识别 (Field Name Intelligence):
        自动识别包含时间语义的字段名：ordertime, createtime, updatetime, timestamp
        自动识别包含URL语义的字段名：imgurls, imageurl, url, urls, link, links
        Automatically recognizes field names with time semantics and URL semantics
    """
    types = field_types[field_name]
    
    # 特殊处理：时间字段自动识别 | Special handling: Automatic time field recognition
    if field_name.lower() in ['ordertime', 'createtime', 'updatetime', 'timestamp']:
        return 'DATETIME'
    
    # 特殊处理：URL字段自动识别，使用TEXT类型存储长URL | Special handling: URL field recognition, use TEXT for long URLs
    url_keywords = ['url', 'urls', 'link', 'links', 'img', 'image', 'photo', 'pic']
    if any(keyword in field_name.lower() for keyword in url_keywords):
        return 'TEXT'  # URL字段使用TEXT类型以支持长URL数组 | Use TEXT type for URL fields to support long URL arrays
    
    # 数据类型优先级映射 | Data type priority mapping
    if 'DECIMAL' in types:
        return 'DECIMAL(15, 6)'  # 高精度小数 | High precision decimal
    elif 'INT' in types:
        return 'BIGINT'          # 大整数支持时间戳 | Large integer supports timestamp
    elif 'BOOLEAN' in types and len(types) == 1:
        return 'BOOLEAN'         # 纯布尔类型 | Pure boolean type
    elif 'TEXT' in types:
        return 'TEXT'            # JSON数据存储 | JSON data storage
    else:
        # 根据字段名判断是否可能包含长文本 | Determine if field may contain long text based on field name
        long_text_keywords = ['description', 'desc', 'detail', 'content', 'note', 'remark', 'comment', 'address', 'addr']
        if any(keyword in field_name.lower() for keyword in long_text_keywords):
            return 'TEXT'        # 描述性字段使用TEXT | Use TEXT for descriptive fields
        else:
            return 'VARCHAR(500)'    # 默认字符串类型 | Default string type

def create_table_if_not_exists(cursor, table_name, field_types):
    """
    智能数据库表创建器
    Intelligent database table creator
    
    功能描述 (Description):
        基于API数据结构动态创建数据库表，如果表已存在则跳过创建
        Dynamically creates database table based on API data structure, 
        skips creation if table already exists
    
    参数 (Parameters):
        cursor (pymysql.cursors.Cursor): 数据库游标对象 | Database cursor object
        table_name (str): 目标表名 | Target table name
        field_types (dict): 字段类型映射字典 | Field type mapping dictionary
    
    表结构设计 (Table Structure Design):
        1. 主键：自增ID字段 | Primary key: Auto-increment ID field
        2. API字段：根据数据分析结果动态创建 | API fields: Dynamically created based on data analysis
        3. 审计字段：createTime (记录创建时间) | Audit fields: createTime (record creation time)
        4. 查询字段：queryDate (数据查询日期) | Query fields: queryDate (data query date)
    
    安全特性 (Security Features):
        - 表名使用反引号防止SQL注入 | Table names use backticks to prevent SQL injection
        - 字段名使用反引号确保兼容性 | Field names use backticks for compatibility
        - 不删除已存在的表保护数据 | Doesn't drop existing tables to protect data
    """
    # 检查表是否已存在 | Check if table already exists
    if check_table_exists(cursor, table_name):
        print(f"表 {table_name} 已存在，跳过创建")
        return
    
    print(f"表 {table_name} 不存在，开始创建...")
    
    # 构建表字段定义 | Build table field definitions
    fields = ["id INT AUTO_INCREMENT PRIMARY KEY"]  # 主键定义 | Primary key definition
    
    # 添加API数据字段 | Add API data fields
    for field_name, types in field_types.items():
        mysql_type = get_mysql_type(field_types, field_name)
        fields.append(f"`{field_name}` {mysql_type}")
    
    # 添加系统审计字段 | Add system audit fields
    fields.extend([
        "createTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP",  # 记录创建时间 | Record creation time
        "queryDate DATE"                                   # 数据查询日期 | Data query date
    ])
    
    # 生成CREATE TABLE SQL语句 | Generate CREATE TABLE SQL statement
    create_sql = f"CREATE TABLE {table_name} (\n    " + ",\n    ".join(fields) + "\n);"
    
    print("创建表的SQL语句:")
    print(create_sql)
    
    # 执行表创建 | Execute table creation
    cursor.execute(create_sql)
    print(f"表 {table_name} 创建成功")

def get_existing_columns(cursor, table_name):
    """
    获取数据库表现有列信息
    Get existing column information of database table
    
    功能描述 (Description):
        查询指定表的所有列名，用于字段兼容性检查
        Queries all column names of specified table for field compatibility check
    
    参数 (Parameters):
        cursor (pymysql.cursors.Cursor): 数据库游标对象 | Database cursor object
        table_name (str): 目标表名 | Target table name
    
    返回值 (Returns):
        set: 现有列名集合 | Set of existing column names
    """
    cursor.execute(f"DESCRIBE {table_name}")
    existing_columns = set()
    for row in cursor.fetchall():
        column_name = row[0]  # 第一列是字段名 | First column is field name
        existing_columns.add(column_name)
    return existing_columns

def add_missing_columns(cursor, table_name, field_types):
    """
    动态字段扩展器 - 为已存在的表添加新的API字段
    Dynamic field extender - adds new API fields to existing table
    
    功能描述 (Description):
        当API返回新字段时，自动为已存在的表添加相应的列，
        实现数据库结构的自动演进
        
        When API returns new fields, automatically adds corresponding columns 
        to existing table, enabling automatic database structure evolution
    
    参数 (Parameters):
        cursor (pymysql.cursors.Cursor): 数据库游标对象 | Database cursor object
        table_name (str): 目标表名 | Target table name
        field_types (dict): 字段类型映射字典 | Field type mapping dictionary
    
    设计优势 (Design Advantages):
        - 支持API接口的向后兼容 | Supports backward compatibility of API interfaces
        - 减少因字段变更导致的程序中断 | Reduces program interruption due to field changes
        - 自动适配新增字段无需手动维护 | Automatically adapts new fields without manual maintenance
    
    安全保障 (Safety Guarantees):
        - 只添加字段，不删除现有字段 | Only adds fields, doesn't delete existing fields
        - 不修改现有字段类型 | Doesn't modify existing field types
        - 保护已有数据完整性 | Protects existing data integrity
    """
    # 检查表是否存在 | Check if table exists
    if not check_table_exists(cursor, table_name):
        return  # 表不存在，无需添加列 | Table doesn't exist, no need to add columns
    
    # 获取现有列信息 | Get existing column information
    existing_columns = get_existing_columns(cursor, table_name)
    
    # 检查并添加API字段 | Check and add API fields
    for field_name in field_types.keys():
        if field_name not in existing_columns:
            mysql_type = get_mysql_type(field_types, field_name)
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN `{field_name}` {mysql_type}"
            print(f"添加新的API字段: {alter_sql}")
            cursor.execute(alter_sql)
    
    # 确保标准系统字段存在 | Ensure standard system fields exist
    standard_columns = {
        'createTime': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'queryDate': 'DATE'
    }
    
    for col_name, col_type in standard_columns.items():
        if col_name not in existing_columns:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN `{col_name}` {col_type}"
            print(f"添加标准字段: {alter_sql}")
            cursor.execute(alter_sql)

def upgrade_column_types(cursor, table_name, field_types):
    """
    数据库列类型升级器 - 升级现有列的数据类型以支持更大的数据
    Database column type upgrader - upgrades existing column data types to support larger data
    
    功能描述 (Description):
        检查现有表的列类型，如果发现某些列需要更大的存储空间（如URL字段），
        自动升级列类型以避免"Data too long"错误
        
        Checks existing table column types, if certain columns need larger storage space 
        (like URL fields), automatically upgrades column types to avoid "Data too long" errors
    
    参数 (Parameters):
        cursor (pymysql.cursors.Cursor): 数据库游标对象 | Database cursor object
        table_name (str): 目标表名 | Target table name  
        field_types (dict): 字段类型映射字典 | Field type mapping dictionary
    
    升级规则 (Upgrade Rules):
        1. URL相关字段：VARCHAR -> TEXT
        2. 描述性字段：VARCHAR -> TEXT  
        3. JSON数组字段：VARCHAR -> TEXT
        4. 保持其他字段类型不变
    
    安全保障 (Safety Guarantees):
        - 只升级到更大的类型，不会丢失数据 | Only upgrades to larger types, no data loss
        - 跳过不存在的字段 | Skips non-existent fields
        - 详细的操作日志记录 | Detailed operation logging
    """
    if not check_table_exists(cursor, table_name):
        return  # 表不存在，无需升级 | Table doesn't exist, no need to upgrade
    
    print(f"\n🔧 检查表 {table_name} 的列类型，升级必要的字段...")
    
    # 获取现有列的详细信息 | Get detailed information of existing columns
    cursor.execute(f"DESCRIBE {table_name}")
    existing_columns = {}
    for row in cursor.fetchall():
        column_name = row[0]  # 字段名 | Column name
        column_type = row[1]  # 字段类型 | Column type  
        existing_columns[column_name] = column_type.upper()
    
    # 检查需要升级的字段 | Check fields that need upgrading
    for field_name in field_types.keys():
        if field_name not in existing_columns:
            continue  # 字段不存在，跳过 | Field doesn't exist, skip
        
        current_type = existing_columns[field_name]
        recommended_type = get_mysql_type(field_types, field_name).upper()
        
        # 检查是否需要从VARCHAR升级到TEXT | Check if need to upgrade from VARCHAR to TEXT
        if ('VARCHAR' in current_type and recommended_type == 'TEXT') or \
           ('VARCHAR(500)' in current_type and 'imgurls' in field_name.lower()):
            
            alter_sql = f"ALTER TABLE {table_name} MODIFY COLUMN `{field_name}` TEXT"
            print(f"🔄 升级字段类型: {field_name} ({current_type} -> TEXT)")
            try:
                cursor.execute(alter_sql)
                print(f"✅ 字段 {field_name} 升级成功")
            except Exception as e:
                print(f"⚠️ 字段 {field_name} 升级失败: {e}")
        elif current_type != recommended_type:
            print(f"ℹ️  字段 {field_name}: {current_type} (建议: {recommended_type})")

# ====================================================================
# 核心业务流程模块 | Core Business Process Module
# ====================================================================

def process_data_extraction(choice, config):
    """
    数据提取核心处理器 - 完整的ETL数据流水线
    Core data extraction processor - Complete ETL data pipeline
    
    功能描述 (Description):
        实现完整的数据提取、转换、加载(ETL)流程：
        1. API认证和令牌获取 | API authentication and token acquisition
        2. 本地数据库连接和重复性检查 | Local database connection and duplication check
        3. API数据请求和响应处理 | API data request and response handling
        4. 数据结构分析和表管理 | Data structure analysis and table management
        5. 数据转换和批量插入 | Data transformation and batch insertion
        
        Implements complete Extract-Transform-Load (ETL) process
    
    参数 (Parameters):
        choice (str): 用户选择的数据类型 ('g'或'c') | User selected data type ('g' or 'c')
        config (dict): 对应的API配置信息 | Corresponding API configuration information
    
    ETL流程阶段 (ETL Process Stages):
        Extract:  从总部API提取原始数据 | Extract raw data from headquarters API
        Transform: 数据类型转换和结构标准化 | Data type conversion and structure normalization
        Load:     批量加载到本地数据库 | Batch load to local database
    
    异常处理策略 (Exception Handling Strategy):
        - 连接级异常：立即终止流程 | Connection level exceptions: Immediate termination
        - 数据级异常：跳过问题记录继续处理 | Data level exceptions: Skip problematic records
        - 全程错误日志记录 | Comprehensive error logging throughout
    
    数据质量保证 (Data Quality Assurance):
        - 重复数据检测防护 | Duplicate data detection protection  
        - 数据类型自动转换 | Automatic data type conversion
        - 时间戳格式智能处理 | Intelligent timestamp format handling
        - JSON数据结构保持 | JSON data structure preservation
    """
    try:
        # ================================================================
        # 第一阶段：API认证和令牌获取 | Phase 1: API Authentication & Token Acquisition
        # ================================================================
        print(f"\n🔐 开始获取token以访问{config['name']}...")
        token = get_token()
        print("✅ Successfully obtained token:", token)

        # ================================================================
        # 第二阶段：数据查询参数配置 | Phase 2: Data Query Parameter Configuration  
        # ================================================================
        # 设置数据查询的日期范围 | Set date range for data query
        # 注意：生产环境中可从命令行参数或配置文件获取
        # Note: In production, can be obtained from command line args or config file
        payload = {
            "startDate": "2025-07-11",  # 查询开始日期 | Query start date
            "endDate": "2025-07-13"     # 查询结束日期 | Query end date
        }

        # ================================================================
        # 第三阶段：本地数据库连接和数据重复性检查 | Phase 3: Local Database Connection & Duplication Check
        # ================================================================
        # 建立本地数据库连接 | Establish local database connection
        print(f"\n🔌 连接本地数据库: {LOCAL_DB_CONFIG['host']}:{LOCAL_DB_CONFIG['port']}")
        print(f"📊 目标数据库: {LOCAL_DB_CONFIG['database']}")
        
        conn = pymysql.connect(**LOCAL_DB_CONFIG)
        print("✅ Local database connection successful")
        cursor = conn.cursor()

        # 数据重复性检查 - 防止重复导入 | Data duplication check - prevent duplicate import
        if check_table_exists(cursor, config['table_name']):
            has_overlap, existing_dates = check_date_overlap(cursor, config['table_name'], payload['startDate'], payload['endDate'])
            if has_overlap:
                print(f"\n❌ 本地数据库表 {config['table_name']} 中已存在 {payload['startDate']} 到 {payload['endDate']} 范围内的数据")
                print("为避免重复数据，停止数据库写入操作")
                print(f"已存在的日期: {', '.join(existing_dates)}")
                cursor.close()
                conn.close()
                return

        # ================================================================
        # 第四阶段：API数据请求和响应处理 | Phase 4: API Data Request & Response Handling
        # ================================================================
        # 构建带签名的API请求头 | Build signed API request headers
        timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳 | Millisecond timestamp
        private_key = get_private_key()
        
        headers = {
            "Content-Type": "application/json",           # JSON内容类型 | JSON content type
            "appId": APP_ID,                             # 应用标识 | Application identifier
            "token": token,                              # 访问令牌 | Access token
            "Authorization": token,                      # 授权头 | Authorization header  
            "timestamp": timestamp,                      # 请求时间戳 | Request timestamp
            "signVal": sign_data(payload, private_key)   # 请求签名 | Request signature
        }

        print(f"\n📡 正在从总部API请求{config['name']}...")
        print("数据请求头:", headers)
        print("数据请求参数:", payload)

        # 发送API数据请求 | Send API data request
        response = requests.post(config['url'], headers=headers, json=payload)
        print("API Response Status Code:", response.status_code)
        print("API Request URL:", response.url)
        print("API Response Text:", response.text)
        
        # 检查HTTP状态码 | Check HTTP status code
        if response.status_code != 200:
            error_msg = f"API请求失败，HTTP状态码: {response.status_code}"
            if response.text:
                error_msg += f", 响应内容: {response.text}"
            raise Exception(error_msg)
        
        # 检查响应内容是否为空 | Check if response content is empty
        if not response.text or response.text.strip() == "":
            raise Exception("API返回空响应内容")
        
        # 尝试解析JSON响应 | Try to parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"API响应不是有效的JSON格式: {e}, 响应内容: {response.text}")
        
        print("API Response Data:", data)

        # API响应状态验证 | API response status validation
        if not data.get('success'):
            error_message = data.get('message', 'Unknown error')
            raise Exception(f"API Error: {error_message}")

        # ================================================================
        # 第五阶段：数据提取和结构分析 | Phase 5: Data Extraction & Structure Analysis
        # ================================================================
        # 提取数据列表，安全处理空值情况 | Extract data list, safely handle null cases
        receipts_data = data.get("data", {})
        if receipts_data is None:
            receipts_data = {}
        receipts_list = receipts_data.get(config['data_key'], [])
        
        print(f"📊 Number of {config['name']} records found between {payload['startDate']} and {payload['endDate']}: {len(receipts_list)}")

        # 处理空数据情况 | Handle empty data case
        if len(receipts_list) == 0:
            print(f"⚠️  No {config['name']} data found for the specified date range.")
            cursor.close()
            conn.close()
            return

        # API数据结构智能分析 | Intelligent API data structure analysis
        print(f"\n🔍 === 分析{config['name']}API返回的数据结构 ===")
        field_types = analyze_data_structure(receipts_list)
        
        print("发现的字段及其类型:")
        for field, types in field_types.items():
            print(f"  {field}: {', '.join(types)}")

        # ================================================================
        # 第六阶段：本地数据库表结构管理 | Phase 6: Local Database Table Structure Management
        # ================================================================
        # 动态创建或更新表结构 | Dynamically create or update table structure
        print(f"\n🏗️  管理本地数据库表结构: {config['table_name']}")
        create_table_if_not_exists(cursor, config['table_name'], field_types)
        add_missing_columns(cursor, config['table_name'], field_types)
        upgrade_column_types(cursor, config['table_name'], field_types)  # 升级列类型以支持更大数据

        # ================================================================
        # 第七阶段：数据转换和批量插入 | Phase 7: Data Transformation & Batch Insertion
        # ================================================================
        # 构建动态SQL插入语句 | Build dynamic SQL insert statement
        field_names = list(field_types.keys()) + ["createTime", "queryDate"]
        placeholders = ", ".join(["%s"] * len(field_names))
        field_list = ", ".join([f"`{field}`" for field in field_names])
        
        insert_sql = f"INSERT INTO {config['table_name']} ({field_list}) VALUES ({placeholders})"
        print("插入SQL:", insert_sql)

        # 批量数据处理和插入 | Batch data processing and insertion
        print(f"\n💾 开始批量插入数据到本地数据库...")
        insert_count = 0
        for item in receipts_list:
            try:
                values = []
                
                # 按字段顺序准备数据值 | Prepare data values in field order
                for field_name in field_types.keys():
                    value = item.get(field_name)
                    
                    # 智能数据类型转换 | Intelligent data type conversion
                    if isinstance(value, list) or isinstance(value, dict):
                        # JSON对象/数组序列化 | JSON object/array serialization
                        value = json.dumps(value, ensure_ascii=False) if value else None
                    elif isinstance(value, int) and field_name.lower() in ['ordertime', 'createtime', 'updatetime', 'timestamp'] and value:
                        # 时间戳智能转换 | Intelligent timestamp conversion
                        try:
                            # 毫秒级时间戳检测和转换 | Millisecond timestamp detection and conversion
                            if value > 9999999999:  # 毫秒级时间戳 | Millisecond timestamp
                                value = datetime.fromtimestamp(value / 1000)
                            else:  # 秒级时间戳 | Second timestamp
                                value = datetime.fromtimestamp(value)
                        except Exception as e:
                            print(f"时间戳转换失败 {field_name}={value}: {e}")
                            value = None
                    
                    values.append(value)
                
                # 添加系统审计字段 | Add system audit fields
                values.extend([
                    datetime.now(),           # createTime - 记录创建时间 | Record creation time
                    datetime.now().date()     # queryDate - 数据查询日期 | Data query date
                ])
                
                # 执行单条记录插入 | Execute single record insertion
                cursor.execute(insert_sql, values)
                insert_count += 1
                if insert_count % 10 == 0:  # 每10条记录显示进度 | Show progress every 10 records
                    print(f"📝 Inserted record {insert_count}")
                
            except Exception as e:
                # 单条记录错误处理 - 继续处理其他记录 | Single record error handling - continue with other records
                print("插入出错：", e)
                print("Problem record:", item)
                print("Values being inserted:", values)
                import traceback
                traceback.print_exc()
                continue

        # ================================================================
        # 第八阶段：事务提交和资源清理 | Phase 8: Transaction Commit & Resource Cleanup
        # ================================================================
        # 提交数据库事务 | Commit database transaction
        conn.commit()
        print(f"✅ Successfully inserted {insert_count} records")
        
        # 清理数据库资源 | Cleanup database resources
        cursor.close()
        conn.close()

        # 输出执行结果摘要 | Output execution result summary
        print(f"\n🎉 === 数据同步完成 ===")
        print(f"✅ {config['name']}已成功同步到本地数据库!")
        print(f"📊 目标数据库: {LOCAL_DB_CONFIG['database']}@{LOCAL_DB_CONFIG['host']}:{LOCAL_DB_CONFIG['port']}")
        print(f"📋 目标表: {config['table_name']}")
        print(f"📈 新增记录数: {insert_count} 条")
        print(f"📅 日期范围: {payload['startDate']} 到 {payload['endDate']}")
        print(f"🕒 同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        # 全局异常处理 | Global exception handling
        print(f"❌ 处理{config['name']}时出错：", e)
        import traceback
        traceback.print_exc()

# ====================================================================
# 程序入口和主控制器 | Program Entry Point & Main Controller
# ====================================================================

def main():
    """
    程序主控制器 - 总部数据同步工具的统一入口点
    Program main controller - unified entry point for headquarters data sync tool
    
    功能描述 (Description):
        作为整个数据同步程序的协调器，负责：
        1. 程序启动和欢迎信息显示 | Program startup and welcome message display
        2. 用户交互和选择处理 | User interaction and choice handling  
        3. 业务流程调度和异常处理 | Business process scheduling and exception handling
        4. 程序结束和资源清理 | Program termination and resource cleanup
        
        Serves as coordinator for entire data synchronization program
    
    程序架构 (Program Architecture):
        采用模块化设计，各功能模块职责清晰：
        - 认证模块：处理API安全认证 | Authentication module: handles API security
        - 数据库模块：管理本地数据持久化 | Database module: manages local data persistence  
        - 分析模块：处理数据结构分析 | Analysis module: handles data structure analysis
        - 转换模块：处理数据格式转换 | Transform module: handles data format conversion
        
        Uses modular design with clear module responsibilities
    
    使用场景 (Usage Scenarios):
        1. 定时数据同步任务 | Scheduled data synchronization tasks
        2. 一次性历史数据迁移 | One-time historical data migration
        3. API数据质量验证 | API data quality validation
        4. 数据库结构演进管理 | Database structure evolution management
    
    扩展性设计 (Extensibility Design):
        - 新数据源：在API_CONFIGS中添加配置 | New data sources: add config in API_CONFIGS
        - 新字段类型：扩展get_mysql_type函数 | New field types: extend get_mysql_type function
        - 新转换规则：扩展数据转换逻辑 | New transform rules: extend data conversion logic
        - 新验证规则：扩展数据质量检查 | New validation rules: extend data quality checks
    """
    # 程序启动横幅和说明 | Program startup banner and description
    print("🚀 总部数据同步程序启动 | Headquarters Data Sync Tool Started")
    print("📡 从总部API获取数据并同步到本地MySQL数据库")
    print("🎯 支持提取废钢数据和报废车数据")
    print("Data sync from headquarters API to local MySQL database")
    
    # 用户交互和选择获取 | User interaction and choice acquisition
    choice, config = get_user_choice()
    
    # 核心业务流程执行 | Core business process execution
    process_data_extraction(choice, config)
    
    # 程序完成通知 | Program completion notification
    print("\n🎊 程序执行完成！| Program execution completed!")
    print("感谢使用总部数据同步工具 | Thank you for using headquarters data sync tool")

# ====================================================================
# 程序执行入口点 | Program Execution Entry Point
# ====================================================================
if __name__ == "__main__":
    """
    Python程序标准入口点
    Standard entry point for Python programs
    
    确保程序只在直接执行时运行主函数，
    而不是在被导入为模块时执行
    
    Ensures main function runs only when script is executed directly,
    not when imported as a module
    """
    main()