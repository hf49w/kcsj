from bili_user_space import get_bvids, save_bvids_to_csv
from bili_user import run_all

# 假设user_info是一个字典，其中包含用户信息
user_info = {"name": "51702663"}  # 替换为实际获取的user_info
user_id = user_info.get("name")

# 获取bvid列表并保存到CSV文件
bvid_list = get_bvids(user_id)
save_bvids_to_csv(bvid_list)

# 调用bili_user.py中的函数来运行其他脚本
run_all(user_id)
