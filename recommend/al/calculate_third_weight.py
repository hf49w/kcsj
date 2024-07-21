import pandas as pd
import sqlite3

def get_last_user_records(user_db_path, user_data_table, num_records):
    conn = sqlite3.connect(user_db_path)
    query = f"SELECT * FROM {user_data_table} ORDER BY rowid DESC LIMIT {num_records}"
    last_records = pd.read_sql_query(query, conn)
    conn.close()
    return last_records

def calculate_third_weight(data, user_interested_partition, history_data, user_db_path, user_data_table):
    # 创建分区权重字典
    partition_weights = {
        '动物圈': 1,
        '美食': 1,
        '资讯': 1,
        '娱乐': 1,
        '动画': 1,
        '知识': 1,
        '生活': 1,
        '影视': 1,
        '运动': 1,
        '时尚': 1,
        '番剧': 1,
        '国创': 1,
        '未知': 1,
        '游戏': 1,
        '音乐': 1,
        '科技': 1,
        '汽车': 1,
        '纪录片': 1,
        '舞蹈': 1,
        '电视剧': 1,
        '电影': 1,
        '鬼畜': 1,
    }
    
    category_counts = history_data['category'].value_counts().to_dict()

    for category, count in category_counts.items():
        if category in partition_weights:
            partition_weights[category] += count * 2

    # 获取用户最近的三条记录
    last_user_records = get_last_user_records(user_db_path, user_data_table, 3)

    weight_factor = [10, 4, 2]  # 权重因子

    # 更新分区权重字典
    for i, record in last_user_records.iterrows():
        category = record['category']
        if category in partition_weights:
            partition_weights[category] += weight_factor[i]  # 使用不同的权重因子进行调整

    # 设置用户感兴趣分区的权重
    for partition in user_interested_partition:
        if partition in partition_weights:
            partition_weights[partition] =partition_weights[partition] * 2 + 60
    
    # 根据分区为每个视频分配权重
    data['第三权重'] = data['v_class'].apply(lambda x: partition_weights.get(x, 1))
    
    return data
