from django.http import HttpResponse,Http404
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.shortcuts import render
import json

from .bili_user_space import get_bvids, save_bvids_to_csv
from .bili_user import run_all
from .bili_user_name import fetch_user_name
import sys

def login(request):
    if request.method =='GET':
        pass
        #TODO
        #return HttpResponse("index.html")
        return HttpResponse("dan")
    elif request.method =='POST':
        
        u_id = request.get("userId")
        like = request.get("option1")
        collect = request.get("option2")
        coin = request.get("option3")
        #TODO
        #id_not_found,u_name,like_videos,collect_video,coin_video = search_id(u_id,like,collect,coin)
        #实现查找用户信息函数
        
        #recommemd()
        #实现推荐视频函数，返回给前端react
        #返回视频url
        return HttpResponse("dan")

def test(request):
    raise Http404("damn!")
    # html = "damn!"
    # return HttpResponse(html)

from rest_framework.response import Response
def index(request):
    if request.method == 'POST':
        r_data = {"message":"信息接收成功index",
                  }
        return(Response(r_data))
    return render(request, 'index.html')


def submit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        # 在这里处理数据，比如保存到数据库
        #return JsonResponse({'status': 'success'}, status=200)
        return HttpResponseRedirect("")
    return JsonResponse({'status': 'failed'}, status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def receive_user_info(request):
    sys.stdout.flush()

    print("Received request", flush=True)  # Debugging statement

    # 接收用户信息
    user_info = request.data.get('user_info')  # name, email, message

    # 检查 user_info 是否为空
    if not user_info:
        return Response({"error": "No user info provided"}, status=400)

    # 处理用户信息（可以添加更多逻辑）
    print(f"Received user info: {user_info}", flush=True)

    user_id = (user_info.get("name"))

    if user_id:
        fetch_user_name(user_id)
        # 获取bvid列表并保存到CSV文件
        bvid_list = get_bvids(user_id)
        save_bvids_to_csv(bvid_list)

        # 调用bili_user.py中的函数来运行其他脚本
        run_all(user_id)
    else:
        print("User ID not found in user_info", flush=True)

    

    #bili_user_script='C:/Users/dell/Desktop/bilibili_backend/bilibili_backend/bili_user.py'
    s = ""
    with open(r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt","r") as f:
        s = f.read()
    sys.stdout.flush()

    # 准备响应数据
    response_data = {
        "message": "信息接收成功",
        "name": s,
        "email": user_info.get("email"),
        #"message": user_info.get("message")
    }

    # 打印请求数据用于调试
    print(request.data, flush=True)

    sys.stdout.flush()

    return Response(response_data)


def recommend_return(request):
    #run recommend func
    response_data = {
        "urls":[]
    }
    return Response(response_data)

@api_view(['POST'])
def recommend_preference(request):
    #run recommend func with prefer
    response_data = {
        "urls":[]
    }
    return Response(response_data)

@api_view(['POST'])
def receive_selected_categories(request):
    categories = request.data.get('categories', [])
    print('Received categories:', categories, flush=True)
    # 在这里处理接收到的数据，例如保存到数据库
    with open(r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt","r") as f:
        s = f.read()
    sys.stdout.flush()

    if s != "":
        #传入用户偏好参数！！！！！！！！！！！！！！！！！！！！！！！！！！！
        from .weight_task import run_weight_algorithm_task
        from recommend.bili_recommend_crawler import get_pic_url,get_pic_urls_and_download,get_random_user_agent,download_image
        #爬图片
        v_urls,v_titles,video_views,video_likes,video_intro = run_weight_algorithm_task(categories)
        save_dir = r"C:\Users\dell\Desktop\bilibili_backend\static\images"
        pic_urls = get_pic_urls_and_download(v_urls, save_dir)
        sys.stdout.flush()

        print("pic_urls:",len(pic_urls), flush=True)

    else:
        v_urls,v_titles,video_views,video_likes,v_titles,video_intro = "","","","","",""
    sys.stdout.flush()

    return Response({'status': 'success', 
                     'received_categories': categories,
                     "recommendations": v_urls,
                      "titles": v_titles,
                       "views":video_views,
                       "likes":video_likes,
                       "intro":video_intro,
                         })


from django.http import HttpResponse, Http404
import os

def ImageView(request, image_name):
    abs_path = rf"C:\Users\dell\Desktop\bilibili_backend\static\images\{image_name}.jpg"
    
    try:
        with open(abs_path, 'rb') as image_file:
            a = image_file.read()
            sys.stdout.flush()

            return HttpResponse(a, content_type="image/jpeg")
        
    except FileNotFoundError:
        raise Http404("Image not found")
    

def Image404View(request, image_name):

    raise Http404("Image not found")
