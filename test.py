import requests
import json

url = "http://localhost:5000/api/add_withdrawal"  # 请根据实际情况更改 URL

# 准备需要发送的数据
withdrawal_data = {
    "OrderNumber": "123456789",
    "UserID": "user123",
    "UserAddress": "TVeotNwizfTDNbeQUhoV9koj48eyHC2uYj",
    "Amount": 1,
}

# 发送 POST 请求
try:
    response = requests.post(url, json=withdrawal_data)
    response.raise_for_status()
    print("Withdrawal added successfully")
except requests.exceptions.RequestException as err:
    print(f"Error adding withdrawal: {err}")
