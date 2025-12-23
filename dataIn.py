try:
    import pandas as pd
    import pymysql
    from sqlalchemy import create_engine
    import os
    import sys
    print("所有依赖包导入成功！")
except ImportError as e:
    print(f"导入依赖包失败: {e}")
    print("请运行以下命令安装依赖:")
    print("pip install -r requirements_stable.txt")
    sys.exit(1)

class ExcelToMySQL:
    def __init__(self, host, port, user, password, database):
        """
        初始化数据库连接参数
        """
        self.host = '124.223.182.79'
        self.port = 3306
        self.user = 'root'
        self.password = 'Monica#!wapers0311'
        self.database = 'pls'
        self.connection = None
        self.engine = None
    
    def connect_database(self):
        """
        连接MySQL数据库
        """
        try:
            # 创建数据库连接
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            
            # 创建SQLAlchemy引擎
            # 对密码进行URL编码，防止特殊字符导致连接失败
            import urllib.parse
            encoded_password = urllib.parse.quote_plus(self.password)
            connection_string = f"mysql+pymysql://{self.user}:{encoded_password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(connection_string, echo=True)
            
            print("数据库连接成功！")
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def read_excel_structure(self, file_path, structure_sheet='数据结构'):
        """
        读取Excel文件中的数据结构sheet
        """
        try:
            df_structure = pd.read_excel(file_path, sheet_name=structure_sheet)
            print(f"成功读取数据结构sheet: {structure_sheet}")
            print("数据结构预览:")
            print(df_structure.head())
            print("列名:", df_structure.columns.tolist())
            return df_structure
        except Exception as e:
            print(f"读取数据结构sheet失败: {e}")
            return None
    
    def read_excel_data(self, file_path, data_sheet='具体数值'):
        """
        读取Excel文件中的具体数值sheet
        """
        try:
            df_data = pd.read_excel(file_path, sheet_name=data_sheet)
            print(f"成功读取数据sheet: {data_sheet}")
            print("数据预览:")
            print(df_data.head())
            return df_data
        except Exception as e:
            print(f"读取数据sheet失败: {e}")
            return None
    
    def create_table_from_structure(self, table_name, structure_df):
        """
        根据数据结构创建MySQL表
        """
        try:
            cursor = self.connection.cursor()
            
            # 构建CREATE TABLE语句
            columns = []
            
            # 根据列名来读取数据
            for _, row in structure_df.iterrows():
                # 查找字段名列
                field_name = None
                data_type = None
                comment = None
                
                # 遍历所有列，查找对应的字段
                for col in structure_df.columns:
                    col_lower = str(col).lower().strip()
                    if '字段' in col_lower or 'field' in col_lower:
                        field_name = str(row[col]).strip() if pd.notna(row[col]) else None
                    elif '类型' in col_lower or 'type' in col_lower or '数据类型' in col_lower:
                        data_type = str(row[col]).strip() if pd.notna(row[col]) else None
                    elif '含义' in col_lower or 'comment' in col_lower or '注释' in col_lower or '中文含义' in col_lower:
                        comment = str(row[col]).strip() if pd.notna(row[col]) else None
                
                # 如果没找到列名，使用位置索引（兼容旧格式）
                if field_name is None:
                    field_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
                if data_type is None:
                    data_type = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
                if comment is None and len(row) > 2:
                    comment = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None
                
                # 跳过空行
                if not field_name or field_name == 'nan' or field_name == '':
                    continue
                
                # 处理数据类型映射
                mysql_type = self.map_data_type(data_type)
                
                # 构建列定义
                column_def = f"`{field_name}` {mysql_type}"
                if comment and comment != 'nan' and comment != '':
                    column_def += f" COMMENT '{comment}'"
                
                columns.append(column_def)
                print(f"字段: {field_name}, 类型: {data_type} -> {mysql_type}, 注释: {comment}")
            
            if not columns:
                print("没有找到有效的字段定义")
                return False
            
            # 构建完整的CREATE TABLE语句
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                {', '.join(columns)}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            print(f"创建表 {table_name} 的SQL语句:")
            print(create_sql)
            
            # 执行创建表语句
            cursor.execute(create_sql)
            self.connection.commit()
            print(f"表 {table_name} 创建成功！")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"创建表失败: {e}")
            return False
    
    def map_data_type(self, excel_type):
        """
        将Excel中的数据类型映射为MySQL数据类型
        """
        if not excel_type or excel_type == 'nan':
            return 'VARCHAR(255)'
            
        excel_type_lower = str(excel_type).lower().strip()
        
        # 根据用户要求的数据类型映射
        type_mapping = {
            '整数': 'INT',
            '字符串': 'VARCHAR(255)',
            '对象': 'JSON',
            '数值': 'DECIMAL(10,2)',
            # 兼容其他常见类型
            'varchar': 'VARCHAR(255)',
            'text': 'TEXT',
            'int': 'INT',
            'integer': 'INT',
            'bigint': 'BIGINT',
            'float': 'FLOAT',
            'double': 'DOUBLE',
            'decimal': 'DECIMAL(10,2)',
            'date': 'DATE',
            'datetime': 'DATETIME',
            'timestamp': 'TIMESTAMP',
            'boolean': 'BOOLEAN',
            'bool': 'BOOLEAN',
            'json': 'JSON'
        }
        
        return type_mapping.get(excel_type_lower, 'VARCHAR(255)')
    
    def import_data_to_table(self, table_name, data_df):
        """
        将数据导入到MySQL表中
        """
        try:
            print(f"准备导入数据到表 {table_name}")
            print(f"数据形状: {data_df.shape}")
            print("数据列名:", data_df.columns.tolist())
            print("数据预览:")
            print(data_df.head())
            
            # 清理数据，处理NaN值
            data_df_clean = data_df.fillna('')
            
            # 使用pandas的to_sql方法导入数据
            data_df_clean.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='append',  # 如果表存在则追加数据
                index=False,
                method='multi',
                chunksize=1000  # 分批导入，避免内存问题
            )
            
            print(f"数据成功导入到表 {table_name}，共导入 {len(data_df)} 条记录")
            return True
            
        except Exception as e:
            print(f"导入数据失败: {e}")
            print("尝试使用pymysql直接导入...")
            
            # 如果pandas导入失败，尝试使用pymysql直接导入
            try:
                cursor = self.connection.cursor()
                
                # 获取列名
                columns = data_df.columns.tolist()
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join([f'`{col}`' for col in columns])
                
                # 构建INSERT语句
                insert_sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
                
                # 准备数据
                data_list = []
                for _, row in data_df.iterrows():
                    row_data = []
                    for col in columns:
                        value = row[col]
                        if pd.isna(value):
                            row_data.append(None)
                        else:
                            # 特殊处理JSON字段
                            if col == 'impact':
                                # 将 {5.2, 1.8} 格式转换为有效的JSON格式
                                str_value = str(value).strip()
                                if str_value.startswith('{') and str_value.endswith('}'):
                                    # 提取数字并转换为JSON对象
                                    import re
                                    numbers = re.findall(r'[\d.]+', str_value)
                                    if len(numbers) >= 2:
                                        json_value = f'{{"energy_save": {numbers[0]}, "co2_reduce": {numbers[1]}}}'
                                        row_data.append(json_value)
                                    else:
                                        row_data.append(str_value)
                                else:
                                    row_data.append(str_value)
                            else:
                                row_data.append(str(value))
                    data_list.append(tuple(row_data))
                
                # 批量插入
                cursor.executemany(insert_sql, data_list)
                self.connection.commit()
                cursor.close()
                
                print(f"使用pymysql成功导入 {len(data_list)} 条记录")
                return True
                
            except Exception as e2:
                print(f"pymysql导入也失败: {e2}")
                return False
    
    def process_excel_file(self, file_path, table_name):
        """
        处理单个Excel文件：创建表结构并导入数据
        """
        print(f"\n开始处理文件: {file_path}")
        print(f"目标表名: {table_name}")
        
        # 读取数据结构
        structure_df = self.read_excel_structure(file_path)
        if structure_df is None:
            return False
        
        # 读取具体数据
        data_df = self.read_excel_data(file_path)
        if data_df is None:
            return False
        
        # 创建表结构
        if not self.create_table_from_structure(table_name, structure_df):
            return False
        
        # 导入数据
        if not self.import_data_to_table(table_name, data_df):
            return False
        
        print(f"文件 {file_path} 处理完成！")
        return True
    
    def close_connection(self):
        """
        关闭数据库连接
        """
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        print("数据库连接已关闭")

def main():
    """
    主函数
    """
    # 数据库连接信息
    DB_CONFIG = {
        'host': '124.223.182.79',
        'port': 3306,
        'user': 'root',
        'password': 'Monica#!wapers0311',
        'database': 'pls'
    }
    
    # 创建ExcelToMySQL实例
    excel_to_mysql = ExcelToMySQL(**DB_CONFIG)
    
    # 连接数据库
    if not excel_to_mysql.connect_database():
        return
    
    try:
        # 处理energyAnalysisStrategy.xlsx文件
        file_path = 'data/energyAnalysisStrategy.xlsx'
        table_name = 'energyAnalysisStrategy'
        
        if os.path.exists(file_path):
            excel_to_mysql.process_excel_file(file_path, table_name)
        else:
            print(f"文件不存在: {file_path}")
        
        # 可以在这里添加处理其他Excel文件的代码
        # 例如：
        # excel_to_mysql.process_excel_file('data/otherFile.xlsx', 'otherTable')
        
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        # 关闭数据库连接
        excel_to_mysql.close_connection()

if __name__ == "__main__":
    main()
