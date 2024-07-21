import os
import requests
import pandas as pd
import re
import time
import random
from datetime import datetime
import sqlite3

# 获取当前脚本目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 定义输入文件夹和文件名，转换为绝对路径
folder = os.path.join(script_dir, 'inf')
csv_file = os.path.join(folder, 'user_inf.csv')
user_agents_file = os.path.join(script_dir, 'user-agent.txt')
database_file = os.path.join(script_dir, 'user_data.db')

# 提取BV号的正则表达式
bv_pattern = re.compile(r'BV\w+')

# 读取User-Agent文件
with open(user_agents_file, 'r') as file:
    user_agents = [line.strip() for line in file if line.strip()]

# 随机选择User-Agent
def get_random_user_agent():
    return random.choice(user_agents)

# 忽略SSL证书警告
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 创建数据库连接
conn = sqlite3.connect(database_file)
cursor = conn.cursor()

cursor.execute("DELETE FROM video_info")
conn.commit()

# Create table structure with additional comment fields
cursor.execute('''
    CREATE TABLE IF NOT EXISTS video_info (
        url TEXT PRIMARY KEY,
        last_update_time TEXT,
        tid INTEGER,
        category TEXT,
        tname TEXT,
        title TEXT,
        description TEXT,
        view_count INTEGER,
        danmaku_count INTEGER,
        comment_count INTEGER,
        like_count INTEGER,
        coin_count INTEGER,
        favorite_count INTEGER,
        share_count INTEGER,
        tags TEXT,
        comment1 TEXT,
        comment2 TEXT,
        comment3 TEXT,
        comment4 TEXT,
        comment5 TEXT
    )
''')

category_map = {
    "动画": [1, 24, 25, 27, 47, 86, 210, 253, 257],
    "音乐": [3, 28, 29, 30, 31, 59, 130, 193, 243, 244, 265, 266, 267],
    "游戏": [4, 17, 19, 65, 121, 136, 171, 172, 173],
    "娱乐": [5, 71, 137, 241, 242, 262, 263, 264],
    "电视剧": [11, 185, 187],
    "番剧": [13, 32, 33, 51, 152],
    "电影": [23, 147, 83, 145, 146],
    "知识": [36, 122, 124, 201, 207, 208, 209, 228, 229],
    "鬼畜": [119, 22, 26, 126, 127, 216],
    "舞蹈": [129, 20, 154, 156, 198, 199, 200, 255],
    "时尚": [155, 157, 158, 159, 252],
    "生活": [160, 21, 138, 161, 162, 239, 250, 251, 254],
    "国创": [167, 153, 168, 170, 195],
    "纪录片": [177, 178, 179, 180, 37],
    "影视": [181, 85, 182, 183, 184, 256, 259, 260, 261],
    "科技": [188, 95, 230, 231, 232, 233],
    "资讯": [202, 203, 204, 205, 206],
    "美食": [211, 76, 212, 213, 214, 215],
    "动物圈": [217, 75, 218, 219, 220, 221, 222],
    "汽车": [223, 176, 227, 240, 245, 246, 247, 248, 258],
    "运动": [234, 164, 235, 236, 237, 238, 249]
}

def get_category(tid):
    for category, tids in category_map.items():
        if tid in tids:
            return category
    return '未知'

# 读取user_inf.csv文件
try:
    df = pd.read_csv(csv_file, header=None, low_memory=False, encoding='utf-8-sig')
except pd.errors.EmptyDataError:
    print("CSV文件为空。",flush=True)
    df = pd.DataFrame()  # 创建一个空的DataFrame以便后续处理

# 遍历从第一行开始的URL
for index in range(len(df)):
    url = df.at[index, 0]

    if pd.isna(url):
        continue

    # 检查数据库中是否已存在记录且已更新
    cursor.execute("SELECT last_update_time FROM video_info WHERE url = ?", (url,))
    result = cursor.fetchone()
    if result is not None and pd.notna(result[0]):
        continue

    match = bv_pattern.search(url)
    if not match:
        print(f"URL中未找到BV号: {url}",flush=True)
        continue

    bv_id = match.group()

    # B站API的URL
    api_url = f"https://api.bilibili.com/x/web-interface/view/detail?bvid={bv_id}"

    # 随机选择一个User-Agent
    headers = {
        "User-Agent": get_random_user_agent()
    }

    try:
        # 发送HTTP请求获取视频信息，忽略SSL验证
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        if data['code'] != 0:
            print(f"获取视频信息失败，视频URL: {url}",flush=True)
            continue

        video_data = data['data']['View']

        # Extract necessary information
        tid = video_data['tid']
        tname = video_data['tname']
        title = video_data['title']
        description = video_data['desc']
        danmaku_count = video_data['stat']['danmaku']
        comment_count = video_data['stat']['reply']
        like_count = video_data['stat']['like']
        coin_count = video_data['stat']['coin']
        favorite_count = video_data['stat']['favorite']
        share_count = video_data['stat']['share']
        view_count = video_data['stat']['view']
        tags = ', '.join([tag['tag_name'] for tag in data['data']['Tags']])

        category = get_category(tid)

        # Extract oid for fetching comments
        oid = video_data['aid']

        # Comments API URL
        comments_api_url = f"https://api.bilibili.com/x/v2/reply"
        comments_params = {
            "type": 1,
            "sort": 1,
            "oid": oid
        }

        # Fetch comments
        comments_response = requests.get(comments_api_url, headers=headers, params=comments_params, verify=False)
        comments_response.raise_for_status()
        comments_data = comments_response.json()

        comments = []
        if comments_data['code'] == 0:
            replies = comments_data['data']['replies']
            for reply in replies[:5]:
                comments.append(reply['content']['message'])
        while len(comments) < 5:
            comments.append('-')

        # Insert or update data in the database
        cursor.execute('''
                            INSERT OR REPLACE INTO video_info (url, last_update_time, tid, category, tname, title, description, view_count, danmaku_count, comment_count, like_count, coin_count, favorite_count, share_count, tags, comment1, comment2, comment3, comment4, comment5)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
        url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tid, category, tname, title, description, view_count,
        danmaku_count, comment_count, like_count, coin_count, favorite_count, share_count, tags, comments[0],
        comments[1], comments[2], comments[3], comments[4]))

        # 提交更改到数据库
        conn.commit()

        print(f"成功获取视频信息，视频URL: {url}",flush=True)

        time.sleep(0.1)

    except requests.exceptions.RequestException as e:
        print(f"请求失败，视频URL: {url}, 错误: {e}",flush=True)

# 关闭数据库连接
conn.close()

print(f"信息已成功导出到数据库",flush=True)
