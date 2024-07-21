import sqlite3
import pandas as pd
import os

# 获取当前脚本目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 定义数据库文件和输出文件夹，转换为绝对路径
database_file = os.path.join(script_dir, 'user_data.db')
output_folder = os.path.join(script_dir, 'inf')
output_file = 'user_table.csv'

# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 连接到数据库
conn = sqlite3.connect(database_file)

# 从数据库中读取数据
df = pd.read_sql_query("SELECT * FROM video_info", conn)

# 关闭数据库连接
conn.close()

# 定义输出文件路径
output_file_path = os.path.join(output_folder, output_file)

# 将数据写入CSV文件
df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"信息已成功导出到 {output_file_path}",flush=True)
