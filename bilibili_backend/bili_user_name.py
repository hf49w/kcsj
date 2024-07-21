import os
import requests
import random
import json

# 获取当前脚本目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# Read User-Agent file
user_agents_file = os.path.join(script_dir, 'user-agent.txt')
with open(user_agents_file, 'r') as file:
    user_agents = [line.strip() for line in file if line.strip()]

# Function to get a random User-Agent
def get_random_user_agent():
    return random.choice(user_agents)

# Ignore SSL certificate warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def fetch_user_name(uid):
    api_url = "https://api.vc.bilibili.com/account/v1/user/cards"

    headers = {
        "User-Agent": get_random_user_agent()
    }

    params = {
        "uids": uid
    }

    try:
        # Send HTTP request to get user information, ignore SSL verification
        response = requests.get(api_url, headers=headers, params=params, verify=False)
        response.raise_for_status()  # Check if request was successful

        # Ensure response content is valid JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"无法解析响应内容为JSON，UID: {uid}",flush=True)
            user_name = ''
            # 将输出文件路径改为绝对路径
            user_name_file = r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt" 
            #os.path.join(script_dir, 'user-name.txt')
            with open(user_name_file, 'w') as file:
                file.write(user_name)
            return

        if data['code'] != 0:
            print(f"获取用户信息失败，UID: {uid}，错误代码: {data['code']}",flush=True)
            user_name = ''
            # 将输出文件路径改为绝对路径
            user_name_file = r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt" 
            #os.path.join(script_dir, 'user-name.txt')
            with open(user_name_file, 'w') as file:
                file.write(user_name)
            return

        user_data = data.get('data', [])
        if not user_data:
            print(f"未找到用户信息，UID: {uid}",flush=True)
            user_name = ''
            # 将输出文件路径改为绝对路径
            user_name_file = r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt" 
            #os.path.join(script_dir, 'user-name.txt')
            with open(user_name_file, 'w') as file:
                file.write(user_name)
            return

        user_name = user_data[0].get('name')
        if not user_name:
            print(f"用户信息中未找到用户名，UID: {uid}",flush=True)
            #user_name_file = r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt" 
            #os.path.join(script_dir, 'user-name.txt')
            #with open(user_name_file, 'w') as file:
            #    file.write('')
            user_name = ''
            # 将输出文件路径改为绝对路径
            user_name_file = r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt" 
            #os.path.join(script_dir, 'user-name.txt')
            with open(user_name_file, 'w') as file:
                file.write(user_name)
            return

        # 将输出文件路径改为绝对路径
        user_name_file = r"C:\Users\dell\Desktop\bilibili_backend\user-name.txt" 
        #os.path.join(script_dir, 'user-name.txt')
        with open(user_name_file, 'w') as file:
            file.write(user_name)

        print(f"成功获取用户信息，UID: {uid}，用户名: {user_name}",flush=True)

    except requests.exceptions.RequestException as e:
        print(f"请求失败，UID: {uid}，错误: {e}",flush=True)

