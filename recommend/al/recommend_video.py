import pandas as pd
import numpy as np
import threading
import time
import random
import logging
import sqlite3
from queue import Queue
import sys
from recommend.al.calculate_first_weight import calculate_first_weight
from recommend.al.calculate_second_weight import calculate_second_weight
from recommend.al.calculate_third_weight import calculate_third_weight

class VideoRecommender:
    def __init__(self, partition_names, db_path, table_name, user_db_path, user_data_table, total_video_num=21, decay_rate=0.01, recovery_rate=0.002, user_interested_partition=None):
        self.partition_names = partition_names
        self.db_path = db_path
        self.table_name = table_name
        self.user_db_path = user_db_path
        self.user_data_table = user_data_table
        self.total_video_num = total_video_num
        self.decay_rate = decay_rate
        self.recovery_rate = recovery_rate
        self.user_interested_partition = user_interested_partition if user_interested_partition is not None else []
        self.processed_data = pd.DataFrame()
        self.unprocessed_data = Queue()
        self.initial_weights = None
        self.recommended_videos = {}
        self.data_ready = threading.Event()
        self.data_lock = threading.Lock()
        self.processed_batches = []

        # Initialize weight calculation thread
        self.weight_thread = threading.Thread(target=self.calculate_weight_and_save)
        self.weight_thread.daemon = True
        self.weight_thread.start()

    def read_data_from_db(self, conn, table_name, batch_size=10000):
        query = f"SELECT * FROM {table_name} ORDER BY RANDOM()"
        df_iter = pd.read_sql_query(query, conn, chunksize=batch_size)
        return df_iter
    
    def save_data_to_db(self, df):
        conn = sqlite3.connect(self.db_path)
        df.to_sql(self.table_name, conn, if_exists='replace', index=False)
        conn.close()

    def calculate_weight_and_save(self):
        conn = sqlite3.connect(self.db_path)
        user_conn = sqlite3.connect(self.user_db_path)
        data_iter = self.read_data_from_db(conn, self.table_name)
        user_data = pd.read_sql_query(f"SELECT * FROM {self.user_data_table}", user_conn)

        for batch_data in data_iter:
            batch_data = calculate_first_weight(batch_data)
            batch_data = calculate_second_weight(batch_data, user_data, self.user_db_path, self.user_data_table)
            batch_data = calculate_third_weight(batch_data, self.user_interested_partition, user_data, self.user_db_path, self.user_data_table)

            batch_data.loc[:, '权重'] = batch_data['第一权重'] * batch_data['第二权重'] * batch_data['第三权重']

            with self.data_lock:
                self.processed_data = pd.concat([self.processed_data, batch_data], ignore_index=True)
                if self.initial_weights is None:
                    self.initial_weights = self.processed_data['权重'].copy()
                self.data_ready.set()

            logging.info("一批数据的权重已更新")

        conn.close()
        user_conn.close()

    def update_weights(self):
        current_time = time.time()
        
        # 读取用户的历史记录数据库
        user_conn = sqlite3.connect(self.user_db_path)
        user_history = pd.read_sql_query(f"SELECT url FROM {self.user_data_table}", user_conn)
        user_conn.close()
        
        # 获取用户历史记录中的视频URL
        watched_videos = set(user_history['url'])
        
        with self.data_lock:
            # 恢复推荐视频的权重
            for video_id, timestamp in self.recommended_videos.items():
                if video_id in self.processed_data.index:
                    time_diff = current_time - timestamp
                    recovery_factor = 1 + self.recovery_rate * time_diff
                    if video_id in self.initial_weights.index:
                        self.processed_data.loc[video_id, '权重'] = min(
                            self.processed_data.loc[video_id, '权重'] * recovery_factor,
                            self.initial_weights[video_id],
                        )
            
            # 衰减推荐视频的权重
            for video_id in self.recommended_videos.keys():
                if video_id in self.processed_data.index:
                    self.processed_data.loc[video_id, '权重'] *= self.decay_rate
            
            # 降低用户历史记录中视频的权重
            mask = self.processed_data['url'].isin(watched_videos)
            self.processed_data.loc[mask, '权重'] *= self.decay_rate


    def recommend_videos(self):
        if not self.data_ready.is_set():
            logging.warning("数据还未准备好，请稍后再试。")
            return None

        num_interesting_videos = random.randint(2, 3)
        self.update_weights()
        for _ in range(10):  # 最多尝试10次
            try:
                # 获取推荐池内视频数量
                num_videos_in_pool = len(self.processed_data)

                # 获取符合用户兴趣分区的视频
                if self.user_interested_partition:
                    interested_videos = self.processed_data[self.processed_data['v_class'].isin(self.user_interested_partition)]
                else:
                    interested_videos = pd.DataFrame()  # 空数据框

                num_videos_in_interest = len(interested_videos)

                # 计算随机挑选感兴趣视频的上下限
                if num_videos_in_interest > 0:
                    lower_bound_interest = int(0.1 * num_videos_in_interest)
                    upper_bound_interest = int(0.3 * num_videos_in_interest)

                    # 设置随机挑选感兴趣视频的数量和权重范围
                    random_largest_weight_interest = random.randint(lower_bound_interest, upper_bound_interest)

                    # 挑选感兴趣视频
                    top_interesting_videos = interested_videos.nlargest(random_largest_weight_interest, "权重")
                    top_interesting_indices = top_interesting_videos.index
                    top_interesting_probabilities = top_interesting_videos["权重"] / top_interesting_videos["权重"].sum()

                    top_interesting_probabilities = top_interesting_probabilities.fillna(0)

                    selected_interesting_videos = np.random.choice(
                        top_interesting_indices,
                        size=min(num_interesting_videos, len(top_interesting_indices)),
                        replace=False,
                        p=top_interesting_probabilities,
                    )
                else:
                    selected_interesting_videos = []

                # 计算随机挑选所有视频的上下限
                lower_bound_pool = int(0.1 * num_videos_in_pool)
                upper_bound_pool = int(0.3 * num_videos_in_pool)

                # 设置随机挑选所有视频的数量和权重范围
                random_largest_weight_pool = random.randint(lower_bound_pool, upper_bound_pool)
                random_largest_weight_num_pool = random.randint(12, 16)
                other_weight_num_pool = self.total_video_num - random_largest_weight_num_pool - num_interesting_videos

                # 挑选所有视频
                top_100_videos = self.processed_data.nlargest(random_largest_weight_pool, "权重")
                top_100_indices = top_100_videos.index
                top_100_probabilities = top_100_videos["权重"] / top_100_videos["权重"].sum()
                
                top_100_probabilities = top_100_probabilities.fillna(0)

                top_10_from_100 = np.random.choice(
                    top_100_indices,
                    size=min(random_largest_weight_num_pool, len(top_100_indices)),
                    replace=False,
                    p=top_100_probabilities,
                )

                remaining_videos = self.processed_data[~self.processed_data.index.isin(top_100_indices)]
                remaining_probabilities = (
                    remaining_videos["权重"] / remaining_videos["权重"].sum()
                )

                remaining_probabilities = remaining_probabilities.fillna(0)

                remaining_10 = np.random.choice(
                    remaining_videos.index,
                    size=min(other_weight_num_pool, len(remaining_videos)),
                    replace=False,
                    p=remaining_probabilities,
                )

                # 找到 top_10_from_100 中权重最大的一个视频
                top_10_from_100_weights = self.processed_data.loc[top_10_from_100, "权重"]
                max_weight_index = top_10_from_100_weights.idxmax()

                # 将权重最大的那个视频放在第一个位置
                ordered_top_10_from_100 = np.concatenate(([max_weight_index], top_10_from_100[top_10_from_100 != max_weight_index]))

                # 合并推荐视频索引，确保不重复
                recommended_indices_set = set(ordered_top_10_from_100)
                recommended_indices_set.update(remaining_10)
                recommended_indices_set.update(selected_interesting_videos)

                # 确保推荐视频数量达到要求
                if len(recommended_indices_set) < self.total_video_num:
                    remaining_needed = self.total_video_num - len(recommended_indices_set)
                    remaining_all_indices = self.processed_data.index.difference(recommended_indices_set)
                    additional_indices = np.random.choice(
                        remaining_all_indices,
                        size=remaining_needed,
                        replace=False,
                    )
                    recommended_indices_set.update(additional_indices)

                recommended_indices = list(recommended_indices_set)
                recommended_videos_df = self.processed_data.loc[recommended_indices]

                # 找到推荐视频中权重最高的视频并放在第一个位置
                max_weight_video_id = recommended_videos_df["权重"].idxmax()
                max_weight_video_row = recommended_videos_df.loc[max_weight_video_id]
                recommended_videos_df = recommended_videos_df.drop(max_weight_video_id)
                recommended_videos_df = pd.concat([pd.DataFrame([max_weight_video_row], index=[max_weight_video_id]), recommended_videos_df])

                current_time = time.time()
                for video_id in recommended_videos_df.index:
                    self.recommended_videos[video_id] = current_time
            except ValueError as e:
                logging.error(f"推荐视频时出现错误: {e}")
                continue

        return recommended_videos_df

    def save_recommended_videos(self, recommended_videos_df, output_file_path):
        recommended_videos_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        logging.info(f"推荐的 {self.total_video_num} 个视频结果保存到 {output_file_path}")
        sys.stdout.flush()

def initialize_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("recommender.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# Initialize logging
#initialize_logging()

# # Initialize logging
# initialize_logging()

# start_time = time.time()

# # Initialize recommender system
# partition_names = ['动画', '番剧', '国创', '科技', '舞蹈', '知识', '动物圈', '美食', '资讯', '娱乐', '生活', '影视', '运动', '时尚', '未知', '音乐', '鬼畜', '游戏', '汽车', '纪录片', '电视剧', '电影']
# db_path = r'C:\Users\dell\Desktop\bilibili_backend\db.sqlite3'
# table_name = "video"
# user_db_path = r'C:\Users\dell\Desktop\bilibili_backend\bilibili_backend\user_data.db'
# user_data_table = "video_info"
# recommender = VideoRecommender(partition_names, db_path, table_name, user_db_path, user_data_table, user_interested_partition='动画')

# # Start interactive recommendation system
# while True:
#     command = input("请输入指令 ('r' 进行推荐, 'exit' 退出): ")
#     if command.lower() == 'r':
#         recommender.data_ready.wait()
#         recommender.update_weights()
#         print("权重已更新")
#         recommended_videos_df = recommender.recommend_videos()

#         # Calculate time difference
#         end_time = time.time()
#         time_difference = end_time - start_time
#         print(f"推荐操作耗时: {time_difference:.2f} 秒")

#         if recommended_videos_df is not None:
#             recommender.save_recommended_videos(recommended_videos_df, 'recommended_videos.csv')
#             video_urls = recommended_videos_df['url'].tolist()  # Assume video URLs are in the recommendation result
#             print("推荐的视频 URLs:")
#             for url in video_urls:
#                 print(url)
#         else:
#             print("没有可推荐的视频。")
#     elif command.lower() == 'exit':
#         print("退出系统。")
#         break
#     else:
#         print("无效的指令，请重新输入。")
