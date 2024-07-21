# tasks.py
#from celery import shared_task
#import logging
# from recommend.al.recommend_video import VideoRecommender#
# #logger = logging.getLogger(__name__)
# import threading

# # 创建线程局部存储对象
# thread_local = threading.local()


# #@shared_task
# def run_weight_algorithm_task(categories):
#     if len(categories)==0:
#         categories=[]
#     if not hasattr(thread_local, 'recommender'):
#         # Initialize logging
#         #initialize_logging()


#         # Initialize recommender system
#         partition_names = ['动画', '番剧', '国创', '科技', '舞蹈', '知识', '动物圈', '美食', '资讯', '娱乐', '生活', '影视', '运动', '时尚', '未知', '音乐', '鬼畜', '游戏', '汽车', '纪录片', '电视剧', '电影']
#         db_path = r'C:\Users\dell\Desktop\bilibili_backend\db.sqlite3'
#         table_name = "video"
#         user_db_path = r'C:\Users\dell\Desktop\bilibili_backend\bilibili_backend\user_data.db'
#         user_data_table = "video_info"
#         # global recommender
#         thread_local.recommender = VideoRecommender(partition_names, db_path, table_name, user_db_path, user_data_table, user_interested_partition=categories)
#         thread_local.recommender.data_ready.wait()
#         thread_local.recommender.update_weights()
#         print("权重已更新", flush=True)
#         recommended_videos_df = thread_local.recommender.recommend_videos()
#         video_urls = recommended_videos_df['url'].tolist()
#         video_titles = recommended_videos_df['title'].tolist()
#         #print(video_urls)
#         # print("推荐的视频 URLs:")
#         # for url in video_urls:
#         #     print(url)
#     else:
#         thread_local.recommender.data_ready.wait()
#         thread_local.recommender.update_weights()
#         print("权重已更新", flush=True)
#         recommended_videos_df = recommender.recommend_videos()
#         video_urls = recommended_videos_df['url'].tolist()
#         video_titles = recommended_videos_df['title'].tolist()
#     return video_urls,video_titles




# def run_weight_algorithm_task_1():
#     # global recommender
#     recommended_videos_df = thread_local.recommender.recommend_videos()
#     video_urls = recommended_videos_df['url'].tolist()
#     video_titles = recommended_videos_df['title'].tolist()
#     #print(video_urls)
#     # print("推荐的视频 URLs:")
#     # for url in video_urls:
#     #     print(url)
#     return video_urls,video_titles



from recommend.al.recommend_video import VideoRecommender#
re_s = []
def run_weight_algorithm_task(categories):
    if len(categories)==0:
        categories=[]


    partition_names = ['动画', '番剧', '国创', '科技', '舞蹈', '知识', '动物圈', '美食', '资讯', '娱乐', '生活', '影视', '运动', '时尚', '未知', '音乐', '鬼畜', '游戏', '汽车', '纪录片', '电视剧', '电影']
    db_path = r'C:\Users\dell\Desktop\bilibili_backend\db.sqlite3'
    table_name = "video"
    user_db_path = r'C:\Users\dell\Desktop\bilibili_backend\bilibili_backend\user_data.db'
    user_data_table = "video_info"
    # global recommender
    recommender = VideoRecommender(partition_names, db_path, table_name, user_db_path, user_data_table, user_interested_partition=categories)
    recommender.data_ready.wait()
    recommender.update_weights()
    print("权重已更新", flush=True)
    recommended_videos_df = recommender.recommend_videos()
    video_urls = recommended_videos_df['url'].tolist()
    video_titles = recommended_videos_df['title'].tolist()
    video_views = recommended_videos_df['browse'].tolist()
    video_likes = recommended_videos_df['num_likes'].tolist()
    video_intro = recommended_videos_df['intro'].tolist()

    # while True:
    #     print(recommended_videos_df.columns)
    re_s.append(recommender)


    return video_urls,video_titles,video_views,video_likes,video_intro




def run_weight_algorithm_task_1():
    # global recommender
    recommender = re_s[len(re_s) - 1]
    recommended_videos_df = recommender.recommend_videos()
    video_urls = recommended_videos_df['url'].tolist()
    video_titles = recommended_videos_df['title'].tolist()
    video_views = recommended_videos_df['browse'].tolist()
    video_likes = recommended_videos_df['num_likes'].tolist()
    video_intro = recommended_videos_df['intro'].tolist()
    #print(video_urls)
    # print("推荐的视频 URLs:")
    # for url in video_urls:
    #     print(url)
    return video_urls,video_titles,video_views,video_likes,video_intro