import os
import requests
import pandas as pd

# 获取当前脚本目录
script_dir = os.path.dirname(os.path.abspath(__file__))


# 获取 BV 号
def get_bvids(user_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7)"
    }

    bvid_list = []

    try:
        url = 'https://space.bilibili.com/ajax/settings/getSettings'
        params = {'mid': user_id}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Debugging output
        #print(f"Response JSON from getSettings: {data}")

        if 'data' in data and 'privacy' in data['data']:
            privacy = data['data']['privacy']
        else:
            print(f"缺少必要的隐私数据，UID: {user_id}",flush=True)
            return bvid_list

        if privacy.get('likes_video') == 1:
            try:
                url = 'https://api.bilibili.com/x/space/like/video'
                params = {'vmid': user_id}
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                likes_data = response.json()

                # Debugging output
                #print(f"Response JSON from like/video: {likes_data}")

                if 'data' in likes_data and 'list' in likes_data['data']:
                    for item in likes_data['data']['list'][:10]:
                        bvid_list.append(item['bvid'])
            except requests.exceptions.RequestException as e:
                print(f"获取点赞视频失败，UID: {user_id}，错误: {e}",flush=True)
            except (KeyError, ValueError, TypeError) as e:
                print(f"解析点赞视频响应失败，UID: {user_id}，错误: {e}",flush=True)

        if privacy.get('coins_video') == 1:
            try:
                url = 'https://api.bilibili.com/x/space/coin/video'
                params = {'vmid': user_id}
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                coins_data = response.json()

                # Debugging output
                #print(f"Response JSON from coin/video: {coins_data}")

                if 'data' in coins_data:
                    for item in coins_data['data'][:10]:
                        bvid_list.append(item['bvid'])
            except requests.exceptions.RequestException as e:
                print(f"获取投币视频失败，UID: {user_id}，错误: {e}",flush=True)
            except (KeyError, ValueError, TypeError) as e:
                print(f"解析投币视频响应失败，UID: {user_id}，错误: {e}",flush=True)

        if privacy.get('fav_video') == 1:
            try:
                url = 'https://api.bilibili.com/x/v3/fav/folder/created/list-all'
                params = {'up_mid': user_id}
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                fav_folder_data = response.json()

                # Debugging output
                #print(f"Response JSON from fav/folder: {fav_folder_data}")

                if 'data' in fav_folder_data and 'list' in fav_folder_data['data'] and fav_folder_data['data']['list']:
                    folder_id = fav_folder_data['data']['list'][0]['id']
                    url = 'https://api.bilibili.com/x/v3/fav/resource/ids'
                    params = {'media_id': folder_id}
                    response = requests.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    fav_data = response.json()

                    # Debugging output
                    #print(f"Response JSON from fav/resource: {fav_data}")

                    if 'data' in fav_data:
                        for item in fav_data['data'][:10]:
                            bvid_list.append(item['bvid'])
            except requests.exceptions.RequestException as e:
                print(f"获取收藏视频失败，UID: {user_id}，错误: {e}",flush=True)
            except (KeyError, ValueError, TypeError) as e:
                print(f"解析收藏视频响应失败，UID: {user_id}，错误: {e}",flush=True)

    except requests.exceptions.RequestException as e:
        print(f"请求失败，UID: {user_id}，错误: {e}",flush=True)
    except (KeyError, ValueError, TypeError) as e:
        print(f"解析响应失败，UID: {user_id}，错误: {e}",flush=True)

    return bvid_list


def save_bvids_to_csv(bvid_list, output_folder='inf', output_file='user_inf.csv'):
    # 确保输出路径为绝对路径
    output_folder = os.path.join(script_dir, output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file_path = os.path.join(output_folder, output_file)
    df = pd.DataFrame(bvid_list, columns=['bvid'])
    df.to_csv(output_file_path, index=False, header=False, encoding='utf-8-sig')
    print(f"信息已成功导出到 {output_file_path}",flush=True)
    print("爬取结果：",flush=True)
    print(df.head(5),flush=True)

