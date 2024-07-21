import os
import requests
import random
import re
import time
import sys


# 获取脚本所在目录
#script_dir = os.path.dirname(os.path.abspath(__file__))

# 读取 User-Agent 文件
user_agents_file = r"C:\Users\dell\Desktop\bilibili_backend\recommend\user-agent.txt"
#os.path.join(script_dir, 'user-agent.txt')
with open(user_agents_file, 'r') as file:
    user_agents = [line.strip() for line in file if line.strip()]

# 随机选择一个 User-Agent
def get_random_user_agent():
    return random.choice(user_agents)

# 获取 BVID 对应的 pic_url
def get_pic_url(bvid):
    api_url = f"https://api.bilibili.com/x/web-interface/view/detail?bvid={bvid}"
    headers = {"User-Agent": get_random_user_agent()}

    try:
        # 发送 HTTP 请求获取视频信息
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        if data['code'] != 0:
            return "none"

        video_data = data['data']['View']
        return video_data['pic']

    except requests.exceptions.RequestException:
        return "none"

# 下载图片并保存到本地
def download_image(url, save_dir, file_name):
    headers = {"User-Agent": get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
                
        #print(f"Downloaded image to {file_path}", flush=True)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image from {url}: {e}", flush=True)

# 获取图片链接并下载
def get_pic_urls_and_download(bvid_strings, save_dir):
    if len(bvid_strings) < 20:
        raise ValueError("传入的字符串数组必须至少包含20个项")

    bv_pattern = re.compile(r'BV\w+')
    pic_urls = []

    for i, bvid_string in enumerate(bvid_strings):
        match = bv_pattern.search(bvid_string)
        if match:
            bvid = match.group(0)
            pic_url = get_pic_url(bvid)
            pic_urls.append(f"{pic_url}")
            if pic_url != "none":
                file_name = f"{bvid}.jpg"
                download_image(pic_url, save_dir, file_name)
                print
        else:
            pic_urls.append("none")
        time.sleep(0.1)  # 避免频繁请求

    return pic_urls
