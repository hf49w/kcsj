import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

# 定义停用词文件路径
stopwords_path = r'C:\Users\dell\Desktop\bilibili_backend\recommend\al\baidu_stopwords.txt'

# 读取停用词表
with open(stopwords_path, 'r', encoding='utf-8-sig') as f:
    stopwords = set(f.read().splitlines())

# 分词并去除停用词的函数
def preprocess_text(text):
    if not isinstance(text, str):
        text = str(text)
    words = jieba.cut(text)  # 使用jieba进行分词
    filtered_words = [word for word in words if word not in stopwords and word.strip() != '']
    return ' '.join(filtered_words)

# 初始化TfidfVectorizer
vectorizer = TfidfVectorizer()

# 计算词向量的函数
def compute_text_vectors(text_series):
    # 分词并去除停用词
    cleaned_texts = text_series.apply(preprocess_text)
    # 使用TF-IDF生成词向量
    vectors = vectorizer.fit_transform(cleaned_texts)
    return vectors

# 处理历史记录数据并返回分好词的文本串
def process_history_records(history_data):
    # 处理缺失值（将标题、简介、标签的空值替换为空字符串）
    history_data['title'] = history_data['title'].fillna('')
    history_data['description'] = history_data['description'].fillna('')
    history_data['tags'] = history_data['tags'].fillna('')
    
    # 将标题、简介和标签合并为一个文本字段用于生成词向量
    history_data['text'] = history_data['title'] + ' ' + history_data['description'] + ' ' + history_data['tags']
    
    # 分词并去除停用词
    history_data['cleaned_text'] = history_data['text'].apply(preprocess_text)
    
    # 合并所有文本为一个字符串
    combined_text = ' '.join(history_data['cleaned_text'])
    
    return combined_text