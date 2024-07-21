import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import numpy as np

from recommend.al.calculate_history import process_history_records

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import numpy as np
import sqlite3

from recommend.al.calculate_history import process_history_records

# 定义停用词文件路径
stopwords_path = r'C:\Users\dell\Desktop\bilibili_backend\recommend\al\baidu_stopwords.txt' 

# 读取停用词表
with open(stopwords_path, 'r', encoding='utf-8-sig') as f:
    stopwords = set(f.read().splitlines())

# 分词并去除停用词的函数
def preprocess_text(text, stopwords):
    words = jieba.cut(text)  # 使用jieba进行分词
    filtered_words = [word for word in words if word not in stopwords and word.strip() != '']
    return ' '.join(filtered_words)

def get_last_user_records(user_db_path, user_data_table, num_records):
    conn = sqlite3.connect(user_db_path)
    query = f"SELECT * FROM {user_data_table} ORDER BY rowid DESC LIMIT {num_records}"
    last_records = pd.read_sql_query(query, conn)
    conn.close()
    return last_records

def calculate_second_weight(data, history_data, user_db_path, user_data_table):
    # 处理缺失值（将标题、简介、标签的空值替换为空字符串）
    data['title'] = data['title'].fillna('')
    data['intro'] = data['intro'].fillna('')
    data['v_split'] = data['v_split'].fillna('')
    
    # 将标题、简介和标签合并为一个文本字段用于生成词向量
    data['文本'] = data['title'] + ' ' + data['intro'] + ' ' + data['v_split']
    
    # 分词并去除停用词
    data['清洗文本'] = data['文本'].apply(lambda x: preprocess_text(x, stopwords))
    
    # 初始化TfidfVectorizer
    vectorizer = TfidfVectorizer()
    
    # 使用TF-IDF生成每个视频的词向量
    video_vectors = vectorizer.fit_transform(data['清洗文本'])
    
    # 处理用户历史数据
    history_text = process_history_records(history_data)
    history_vectors = vectorizer.transform([history_text])
    
    # 计算输入词向量与每个视频词向量的余弦相似度
    similarity_scores = cosine_similarity(history_vectors, video_vectors).flatten()
    
    # 获取最后三条用户记录
    last_user_records = get_last_user_records(user_db_path, user_data_table, 3)
    
    # 初始化相似度数组
    last_record_similarities = np.zeros((3, len(data)))
    
    if not last_user_records.empty:
        for i, record in last_user_records.iterrows():
            last_record_text = preprocess_text(record['title'] + ' ' + record['description'] + ' ' + record['tags'], stopwords)
            last_record_vector = vectorizer.transform([last_record_text])
            last_record_similarities[i] = cosine_similarity(last_record_vector, video_vectors).flatten()
    else:
        last_record_similarities = np.zeros((3, len(data)))  # 如果没有记录，则相似度为0

    # 将相似度得分作为第二权重，并进行放大处理
    data['第二权重'] = np.exp(similarity_scores * 14 ) - 0.2
    if not last_user_records.empty:
        for i in range(3):
            weight_factor = [15, 14, 14]  # 权重因子
            weight_factor_ = [6, 2, 1]  # 权重因子
            data['第二权重'] += np.exp(last_record_similarities[i] * weight_factor[i]-1)* weight_factor_[i]

    return data
