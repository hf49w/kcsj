import pandas as pd
import numpy as np

def calculate_first_weight(data):
    # 选择用于计算权重的列
    columns_to_consider = ['browse', 'num_likes', 'num_coins', 'num_collect', 'num_share']
    
    # 处理缺失值（用0替换缺失值）
    data[columns_to_consider] = data[columns_to_consider].fillna(0)
    
    # 对每个数据开根号，减少数据差异过大而导致的权重差异过大
    data[columns_to_consider] = data[columns_to_consider].apply(lambda x: np.sqrt(x))
    
    # 计算“互动率” (点赞 + 投币) / 播放量
    # 避免除以零，先将播放量中为0的值设置为一个非常小的值
    data['browse'] = data['browse'].replace(0, 1e-6)
    data['reaction_rate'] = (data['num_likes'] + data['num_coins']) / data['browse']
    
    
    # 添加“互动率”到考虑的列中
    columns_to_consider.append('互动率')
    
    temp = 0.1

    # 原始权重字典
    weights = {
        'browse': 0.05,
        'num_likes': 0.10,
        'num_coins': 0.20,
        'num_collect': 0.1,
        'num_share': 0.1,
        'reaction_rate': 0.0001
    }

    # 将每个权重乘以temp(用来调整第一权重的大小)
    adjusted_weights = {key: value * temp for key, value in weights.items()}
    
    # 计算加权平均值作为第一权重
    data['第一权重'] = (
        data['browse'] * adjusted_weights['browse'] +
        data['num_likes'] * adjusted_weights['num_likes'] +
        data['num_coins'] * adjusted_weights['num_coins'] +
        data['num_collect'] * adjusted_weights['num_collect'] +
        data['num_share'] * adjusted_weights['num_share'] +
        data['reaction_rate'] * adjusted_weights['reaction_rate']
    )
    
    return data
