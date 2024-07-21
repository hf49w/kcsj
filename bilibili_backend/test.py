from bili_user_name import fetch_user_name

user_info = {"id": "2317"}
user_id = user_info.get("id")

if user_id:
    fetch_user_name(user_id)
else:
    print("User ID not found in user_info")
