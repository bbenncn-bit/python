#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库中的数据
"""

try:
    import pandas as pd
    import pymysql
    from sqlalchemy import create_engine
    import json
    print("所有依赖包导入成功！")
except ImportError as e:
    print(f"导入依赖包失败: {e}")
    exit(1)

def verify_data():
    """验证数据库中的数据"""
    print("=== 验证数据库中的数据 ===")
    
    # 数据库连接信息
    host = '124.223.182.79'
    port = 3306
    user = 'root'
    password = 'Monica#!wapers0311'
    database = 'pls'
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 查询表结构
        print("\n1. 表结构:")
        cursor.execute("DESCRIBE energyAnalysisStrategy")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} - {col[5] if col[5] else '无注释'}")
        
        # 查询数据
        print("\n2. 数据内容:")
        cursor.execute("SELECT * FROM energyAnalysisStrategy")
        rows = cursor.fetchall()
        
        print(f"共找到 {len(rows)} 条记录:")
        for i, row in enumerate(rows, 1):
            print(f"\n记录 {i}:")
            print(f"  ID: {row[0]}")
            print(f"  标题: {row[1]}")
            print(f"  描述: {row[2]}")
            print(f"  影响指标: {row[3]}")
            print(f"  操作: {row[4]}")
            
            # 验证JSON字段
            try:
                impact_json = json.loads(row[3])
                print(f"  JSON解析成功: {impact_json}")
            except json.JSONDecodeError as e:
                print(f"  JSON解析失败: {e}")
        
        # 统计信息
        print(f"\n3. 统计信息:")
        cursor.execute("SELECT COUNT(*) FROM energyAnalysisStrategy")
        count = cursor.fetchone()[0]
        print(f"  总记录数: {count}")
        
        cursor.close()
        connection.close()
        
        print("\n✓ 数据验证完成！")
        return True
        
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return False

if __name__ == "__main__":
    verify_data()











