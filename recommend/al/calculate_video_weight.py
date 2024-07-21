import pandas as pd

from recommend.al.calculate_first_weight import calculate_first_weight
from recommend.al.calculate_second_weight import calculate_second_weight
from recommend.al.calculate_third_weight import calculate_third_weight

def calculate_video_weight(data, user_interested_partition, history_data):
    # 计算第一权重
    data = calculate_first_weight(data)
    
    # 计算第二权重
    data = calculate_second_weight(data, history_data)

    # 调用 calculate_third_weight 函数
    data = calculate_third_weight(data, user_interested_partition, history_data)
    
    # 计算最终权重，作为第一权重、第二权重和第三权重的乘积
    data['权重'] = data['第一权重'] * data['第二权重'] * data['第三权重']
    
    # 保存处理后的数据到文件
    output_file_path = 'combined_weighted_all_inf.csv'
    data.to_csv(output_file_path, index=False, encoding='utf-8-sig')
    print(f"处理后的数据已保存到 {output_file_path}", flush=True)