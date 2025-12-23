#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取同步程序 - 自动获取废钢和报废车数据
"""

import requests
import pymysql
from datetime import datetime, timedelta
import json
import base64
import time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# API配置
APP_ID = "PXDP"
ACCESS_KEY = "226b673950704a5c971b236f88948fe1"
PRIVATE_KEY = """MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAICbt0M96LyKMP4bdFMIql+7gbOmXw/K+13qg3IsBdlsEoW7B3yFa9Bffhv1TIOZ7plTAxHy4hV0XbNTotJccmlVk2rq4V3lMCP5O3sbHmNOuewUFrV7A1pewEQIVmETxstrGi2YCcTzjkquI6e7x/CcDuSC+V+rK97EUcNWavz1AgMBAAECgYAnFKqE4Ww21tt6bEdV8B0tyCHqwJTEjM8Dw/67lAsW/dNHFgV5XmXbxRjiUBE3MHCj4Oje7GqtUFYk5zZkLDmLv+uIzCl7f7hnX6eZUA19nY/cSqowZ87K1ZavIIS2wcr6p73MNgTfefFuIpqjnYs4t1Uap5Tj92sD2Icvn9h14QJBAMgC23APecJDw8XS1P4P2KavEHqORaOTm7s8vc2lpxMIqpkIBU15s/YqNURKjMEVR+O+tP5QJy2ba/AWzASKaT0CQQCknAE1Zrn4eoVmwCNPKqv84HpcTNeG7OboStA3yYhQMA2UryobKqmkFALZ1yyjorP/zNZPpDncqb46MV/kUO4ZAkAQ0myyWBrdg+WLVdgkJiEKo9628BBbWabXcJxmF3Cd4TS3+jy372x7X8FrJPoBo1CQjxGZ8hPZeiDx6HjwSNPhAkA+MoA2aFFetRTQ5UqyMCJ6U2uIkrRhVARPw2z3l1u9SNro0mLrjuw4hiMpoqdIUUMIJaLYxuniGfU50cw03euJAkAzk844q1N8WP2H9fVtC7M/FMBfqXZSFk+O96BVboSJNsTqao1slq6ArY47fh0Xfl7e30dSFj8zp/rD1REde8pB"""

API_CONFIGS = {
    'g': {
        'name': '废钢数据',
        'url': 'https://www.oylianjin.com/ecopenapi/basic/a/trade/receipt/query/pingxiang/receipt',
        'table_name': 'receiptfg',
        'data_key': 'fgReceiptDetails'
    },
    'c': {
        'name': '报废车数据',
        'url': 'https://www.oylianjin.com/ecopenapi/basic/a/trade/receipt/query/pingxiang/receipt',
        'table_name': 'receiptfc',
        'data_key': 'fcReceiptDetails'
    }
}

def get_private_key():
    private_key_bytes = base64.b64decode(PRIVATE_KEY.strip())
    private_key = serialization.load_der_private_key(private_key_bytes, password=None)
    return private_key

def sign_data(data_dict, private_key):
    string_dict = {}
    for key, value in data_dict.items():
        if value is None:
            string_dict[key] = "null"
        else:
            string_dict[key] = str(value)
    
    if not string_dict:
        string_dict["sign_val"] = "sign_val"
    
    sorted_keys = sorted(string_dict.keys())
    sign_str = "&".join([f"{k}={string_dict[k]}" for k in sorted_keys])
    
    signature = private_key.sign(
        sign_str.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    
    return base64.b64encode(signature).decode('utf-8')

def get_token():
    token_url = "https://www.oylianjin.com/ecopenapi/open/n/token/gen"
    token_data = {
        "appId": APP_ID,
        "accessKey": ACCESS_KEY
    }
    
    timestamp = str(int(time.time() * 1000))
    private_key = get_private_key()
    
    headers = {
        "Content-Type": "application/json",
        "appId": APP_ID,
        "timestamp": timestamp,
        "signVal": sign_data(token_data, private_key)
    }
    
    response = requests.post(token_url, json=token_data, headers=headers)
    result = response.json()
    
    if not result.get('success'):
        raise Exception(f"获取token失败: {result.get('message')}")
    
    return result.get('data')

# ====================================================================
# 自动同步模块 | Auto Sync Module
# ====================================================================

def get_latest_order_time(cursor, table_name):
    """获取表中最新的orderTime"""
    try:
        cursor.execute(f"""
            SELECT MAX(
                CASE 
                    WHEN orderTime IS NULL THEN NULL
                    WHEN CAST(orderTime AS CHAR) REGEXP '^[0-9]+$' AND CHAR_LENGTH(CAST(orderTime AS CHAR)) > 10 THEN 
                        FROM_UNIXTIME(orderTime/1000)
                    WHEN CAST(orderTime AS CHAR) REGEXP '^[0-9]+$' AND CHAR_LENGTH(CAST(orderTime AS CHAR)) <= 10 THEN 
                        FROM_UNIXTIME(orderTime)
                    ELSE 
                        orderTime
                END
            ) as latest_time
            FROM {table_name}
            WHERE orderTime IS NOT NULL
        """)
        
        result = cursor.fetchone()
        if result and result[0]:
            return result[0].date()
        return None
    except Exception as e:
        print(f"获取{table_name}最新orderTime失败: {e}")
        return None

def check_table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

def analyze_data_structure(data_list):
    all_fields = {}
    for item in data_list:
        for key, value in item.items():
            if key not in all_fields:
                all_fields[key] = set()
            
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
            elif isinstance(value, (list, dict)):
                all_fields[key].add('TEXT')
            else:
                all_fields[key].add('TEXT')
    
    return all_fields

def get_mysql_type(field_types, field_name):
    types = field_types[field_name]
    
    if field_name.lower() in ['ordertime', 'createtime', 'updatetime', 'timestamp']:
        return 'DATETIME'
    
    if 'DECIMAL' in types:
        return 'DECIMAL(15, 6)'
    elif 'INT' in types:
        return 'BIGINT'
    elif 'BOOLEAN' in types and len(types) == 1:
        return 'BOOLEAN'
    elif 'TEXT' in types:
        return 'TEXT'
    else:
        return 'VARCHAR(500)'

def create_table_if_not_exists(cursor, table_name, field_types):
    if check_table_exists(cursor, table_name):
        return
    
    fields = ["id INT AUTO_INCREMENT PRIMARY KEY"]
    
    for field_name, types in field_types.items():
        mysql_type = get_mysql_type(field_types, field_name)
        fields.append(f"`{field_name}` {mysql_type}")
    
    fields.extend([
        "createTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "queryDate DATE"
    ])
    
    create_sql = f"CREATE TABLE {table_name} (\n    " + ",\n    ".join(fields) + "\n);"
    cursor.execute(create_sql)

def get_existing_columns(cursor, table_name):
    cursor.execute(f"DESCRIBE {table_name}")
    existing_columns = set()
    for row in cursor.fetchall():
        existing_columns.add(row[0])
    return existing_columns

def add_missing_columns(cursor, table_name, field_types):
    if not check_table_exists(cursor, table_name):
        return
    
    existing_columns = get_existing_columns(cursor, table_name)
    
    for field_name in field_types.keys():
        if field_name not in existing_columns:
            mysql_type = get_mysql_type(field_types, field_name)
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN `{field_name}` {mysql_type}"
            cursor.execute(alter_sql)
    
    standard_columns = {
        'createTime': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'queryDate': 'DATE'
    }
    
    for col_name, col_type in standard_columns.items():
        if col_name not in existing_columns:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN `{col_name}` {col_type}"
            cursor.execute(alter_sql)

def auto_sync_data():
    """自动同步两个表的数据"""
    print("开始自动同步废钢和报废车数据...")
    
    conn = pymysql.connect(
        host='124.223.182.79',
        port=3306,
        user='root',
        password='Monica#!wapers0311',
        database='pls',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    try:
        # 获取两个表的最新orderTime，取较早的日期作为起始点
        start_dates = {}
        for choice, config in API_CONFIGS.items():
            latest_date = get_latest_order_time(cursor, config['table_name'])
            if latest_date:
                start_dates[choice] = latest_date + timedelta(days=1)
            else:
                start_dates[choice] = datetime(2025, 1, 1).date()
        
        # 取最早的起始日期
        global_start_date = min(start_dates.values())
        current_date = datetime.now().date()
        
        print(f"从 {global_start_date} 开始获取数据")
        
        # 七天一次循环获取数据
        while global_start_date <= current_date:
            end_date = min(global_start_date + timedelta(days=6), current_date)
            
            # 只调用一次API获取数据
            print(f"\n获取数据: {global_start_date} 到 {end_date}")
            api_data = fetch_api_data(global_start_date, end_date)
            
            if api_data:
                # 分别处理废钢和报废车数据
                for choice, config in API_CONFIGS.items():
                    if choice in api_data and api_data[choice]:
                        print(f"处理{config['name']}...")
                        insert_data_to_table(cursor, config, api_data[choice])
            
            global_start_date = end_date + timedelta(days=1)
            time.sleep(1)
    
    finally:
        cursor.close()
        conn.close()
    
    print("\n自动同步完成！")

def fetch_api_data(start_date, end_date):
    """获取API数据，返回包含废钢和报废车数据的字典"""
    try:
        token = get_token()
        
        payload = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d")
        }
        
        timestamp = str(int(time.time() * 1000))
        private_key = get_private_key()
        
        headers = {
            "Content-Type": "application/json",
            "appId": APP_ID,
            "token": token,
            "Authorization": token,
            "timestamp": timestamp,
            "signVal": sign_data(payload, private_key)
        }
        
        print(f"正在获取API数据: {payload['startDate']} 到 {payload['endDate']}")
        
        response = requests.post(API_CONFIGS['g']['url'], headers=headers, json=payload)
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
        
        receipts_data = data.get("data", {}) or {}
        
        # 分别提取废钢和报废车数据
        result = {}
        for choice, config in API_CONFIGS.items():
            data_list = receipts_data.get(config['data_key'], [])
            if data_list:
                result[choice] = data_list
                print(f"获取到 {len(data_list)} 条{config['name']}")
            else:
                result[choice] = []
                print(f"该日期范围内无{config['name']}")
        
        return result
        
    except Exception as e:
        print(f"获取API数据时出错: {e}")
        return None

def insert_data_to_table(cursor, config, data_list):
    """将数据插入到指定表中"""
    try:
        if not data_list:
            return 0
        
        field_types = analyze_data_structure(data_list)
        create_table_if_not_exists(cursor, config['table_name'], field_types)
        add_missing_columns(cursor, config['table_name'], field_types)
        
        field_names = list(field_types.keys()) + ["createTime", "queryDate"]
        placeholders = ", ".join(["%s"] * len(field_names))
        field_list = ", ".join([f"`{field}`" for field in field_names])
        
        insert_sql = f"INSERT INTO {config['table_name']} ({field_list}) VALUES ({placeholders})"
        
        insert_count = 0
        for item in data_list:
            try:
                values = []
                
                for field_name in field_types.keys():
                    value = item.get(field_name)
                    
                    # 特殊处理图片URL字段
                    if field_name.lower() in ['imgurls', 'imgurl', 'imageurl', 'imageurls'] and isinstance(value, list):
                        # 如果是数组且有内容，取第一个元素作为字符串
                        if value and len(value) > 0:
                            value = str(value[0]).strip('"')
                        else:
                            value = None
                    elif isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False) if value else None
                    elif isinstance(value, int) and field_name.lower() in ['ordertime', 'createtime', 'updatetime', 'timestamp'] and value:
                        try:
                            if value > 9999999999:
                                value = datetime.fromtimestamp(value / 1000)
                            else:
                                value = datetime.fromtimestamp(value)
                        except:
                            value = None
                    
                    values.append(value)
                
                values.extend([
                    datetime.now(),
                    datetime.now().date()
                ])
                
                cursor.execute(insert_sql, values)
                insert_count += 1
                
            except Exception as e:
                print(f"插入记录失败: {e}")
                continue
        
        # 提交事务
        cursor.connection.commit()
        print(f"成功插入 {insert_count} 条{config['name']}记录")
        return insert_count
        
    except Exception as e:
        print(f"处理{config['name']}数据时出错: {e}")
        return 0

# ====================================================================
# 程序入口和主控制器 | Program Entry Point & Main Controller
# ====================================================================

def main():
    """
    程序主控制器 - 自动数据同步
    """
    print("🚀 自动数据同步程序启动")
    print("将自动同步废钢和报废车数据")
    print("Auto Data Sync Tool Started - Will sync scrap steel and scrapped vehicle data")
    
    # 执行自动同步
    auto_sync_data()
    
    print("\n程序执行完成！")
    print("Program execution completed!")

if __name__ == "__main__":
    main()