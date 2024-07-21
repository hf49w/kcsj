import os
import subprocess

def run_bili_user_space(user_id):
    result = subprocess.run(
        ['python', r'C:\Users\dell\Desktop\bilibili_backend\bilibili_backend\bili_user_space.py', user_id],
        capture_output=True,
        text=True,
        env={**os.environ, 'PYTHONIOENCODING': 'gbk'}
    )
    print(f"Running bili_user_space.py:\n{result.stdout}\n{result.stderr}",flush=True)

def run_bili_user_crawler(user_id):
    result = subprocess.run(
        ['python', r'C:\Users\dell\Desktop\bilibili_backend\bilibili_backend\bili_user_crawler.py', user_id],
        capture_output=True,
        text=True,
        env={**os.environ, 'PYTHONIOENCODING': 'gbk'}
    )
    print(f"Running bili_user_crawler.py:\n{result.stdout}\n{result.stderr}",flush=True)

def run_bili_user_output(user_id):
    result = subprocess.run(
        ['python', r'C:\Users\dell\Desktop\bilibili_backend\bilibili_backend\bili_user_output.py', user_id],
        capture_output=True,
        text=True,
        env={**os.environ, 'PYTHONIOENCODING': 'gbk'}
    )
    print(f"Running bili_user_output.py:\n{result.stdout}\n{result.stderr}",flush=True)

def run_all(user_id):
    run_bili_user_space(user_id)
    run_bili_user_crawler(user_id)
    run_bili_user_output(user_id)
