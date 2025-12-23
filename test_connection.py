#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接和Excel读取功能
"""

try:
    import pandas as pd
    import pymysql
    from sqlalchemy import create_engine
    import os
    import sys
    import urllib.parse
    print("所有依赖包导入成功！")
except ImportError as e:
    print(f"导入依赖包失败: {e}")
    sys.exit(1)

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    # 数据库连接信息
    host = '124.223.182.79'
    port = 3306
    user = 'root'
    password = 'Monica#!wapers0311'
    database = 'pls'
    
    try:
        # 测试pymysql连接
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        print("✓ pymysql连接成功")
        
        # 测试SQLAlchemy连接
        encoded_password = urllib.parse.quote_plus(password)
        connection_string = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        engine = create_engine(connection_string, echo=False)
        
        # 测试连接
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            print("✓ SQLAlchemy连接成功")
        
        connection.close()
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def test_excel_reading():
    """测试Excel文件读取"""
    print("\n=== 测试Excel文件读取 ===")
    
    file_path = 'data/energyAnalysisStrategy.xlsx'
    
    if not os.path.exists(file_path):
        print(f"✗ 文件不存在: {file_path}")
        return False
    
    try:
        # 读取数据结构sheet
        df_structure = pd.read_excel(file_path, sheet_name='数据结构')
        print("✓ 成功读取数据结构sheet")
        print("列名:", df_structure.columns.tolist())
        print("数据结构预览:")
        print(df_structure.head())
        
        # 读取具体数值sheet
        df_data = pd.read_excel(file_path, sheet_name='具体数值')
        print("\n✓ 成功读取具体数值sheet")
        print("数据形状:", df_data.shape)
        print("数据列名:", df_data.columns.tolist())
        print("数据预览:")
        print(df_data.head())
        
        return True
        
    except Exception as e:
        print(f"✗ Excel读取失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试程序功能...")
    
    # 测试数据库连接
    db_ok = test_database_connection()
    
    # 测试Excel读取
    excel_ok = test_excel_reading()
    
    print("\n=== 测试结果 ===")
    if db_ok and excel_ok:
        print("✓ 所有测试通过！可以运行主程序了。")
        print("运行命令: python dataIn.py")
    else:
        print("✗ 部分测试失败，请检查配置。")
        if not db_ok:
            print("  - 数据库连接有问题")
        if not excel_ok:
            print("  - Excel文件读取有问题")

if __name__ == "__main__":
    main()
