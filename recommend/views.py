from django.shortcuts import render
from recommend.al.recommend_video import VideoRecommender
from bilibili_backend.weight_task import run_weight_algorithm_task_1
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys


@api_view(['GET'])
def recommemd(request):
    sys.stdout.flush()

    if request.method =='GET':
        with open(r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt","r") as f:
            s = f.read()
        if s != "":
            from recommend.bili_recommend_crawler import get_pic_url,get_pic_urls_and_download,get_random_user_agent,download_image
            #爬图片
            v_urls,v_titles,video_views,video_likes,video_intro = run_weight_algorithm_task_1()
            save_dir = r"C:\Users\dell\Desktop\bilibili_backend\static\images"
            pic_urls = get_pic_urls_and_download(v_urls, save_dir)
            sys.stdout.flush()

            print("pic_urls:",len(pic_urls), flush=True)

        else:
            v_urls,v_titles,video_views,v_titles,video_intro = "","","","",""
        sys.stdout.flush()

        return Response({'status': 'success', 
                        "recommendations": v_urls,
                        "titles": v_titles,
                        "views":video_views,
                        "likes":video_likes,
                        "intro":video_intro,
                            })

