from flask import Flask, jsonify, request, render_template
from flask_cors import CORS  # Import CORS module
import mysql.connector
from flask import jsonify
import requests



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '960322iS@'
MYSQL_DB = 'app'

# ... (create_table and other functions remain unchanged)

def create_table():
    conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ordernumber VARCHAR(255),
            userid VARCHAR(255),
            useraddress VARCHAR(255),
            amount INT,
            success INT,
            tx VARCHAR(255),
            confirmed INT
        )
    ''')
    conn.commit()
    conn.close()

create_table()










# 添加一个新的端点用于获取提现数据
# 用于前端显示
@app.route('/api/withdrawals', methods=['GET'])
def get_withdrawals():
    conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM withdrawals')
    withdrawals = cursor.fetchall()
    conn.close()

    return jsonify(withdrawals)









# 添加一个新的端点用于确认提现


@app.route('/api/withdrawals', methods=['POST'])
def confirm_withdrawal():
    try:
        data = request.get_json()
        withdrawal_id = data.get('id')

        # 连接数据库
        conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
        cursor = conn.cursor(dictionary=True)

        # 查询数据库获取 useraddress 和 amount
        cursor.execute('SELECT useraddress, amount FROM withdrawals WHERE id = %s', (withdrawal_id,))
        result = cursor.fetchone()

        if result:
            useraddress = result['useraddress']
            amount = result['amount']

            # 保存接收到的数据到文件
            with open('01htmltopydate.txt', 'a') as file:
                file.write(f"Withdrawal ID: {withdrawal_id}, User Address: {useraddress}, Amount: {amount}\n")

            # 执行确认处理...

            response_data = {"message": "Withdrawal confirmed successfully"}

            # 发送数据到本机端口 3000
            post_data = {'id': withdrawal_id, 'useraddress': useraddress, 'amount': amount}

            with open('02pytojsdate.txt', 'a') as file:
                file.write(f" {post_data}\n")

            try:
                response = requests.post('http://localhost:3000/', json=post_data)
                response.raise_for_status()
                print('Data sent successfully to port 3000')
            except requests.exceptions.RequestException as err:
                print(f'Error sending data to port 3000: {err}')

            return jsonify(response_data), 200
        else:
            return jsonify({"error": "Withdrawal not found"}), 404
    except Exception as e:
        app.logger.error(f"Error confirming withdrawal: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()




# 新建一个用于接收 Node.js 发送数据的 API 端点
@app.route('/api/transfer-data', methods=['POST'])
def receive_transfer_data():
    try:
        data = request.get_json()
        received_id = data.get('idlove')
        received_transfer = data.get('transfer')


        with open('05pyredate.txt', 'a') as file:
                file.write(f" {received_id},{received_transfer}\n")

        # 在这里处理接收到的数据，可以将其保存到数据库或进行其他操作
        # 例如，可以使用 received_id 和 received_transfer 插入到 withdrawals 表中

        # 连接到 MySQL 数据库
        conn = mysql.connector.connect(host='localhost', user='root', password='960322iS@', database='app')
        cursor = conn.cursor(dictionary=True)

        # 更新数据库中的 Transaction ID
        cursor.execute('UPDATE withdrawals SET tx = %s, confirmed = 1 WHERE id = %s', (received_transfer, received_id))
        conn.commit()

        # 关闭数据库连接
        cursor.close()
        conn.close()

        return jsonify({"message": "数据接收成功"}), 200
    except Exception as e:
        app.logger.error(f"接收转账数据时出错: {e}")
        return jsonify({"error": "内部服务器错误"}), 500

# ... (your existing code remains unchanged)





# 添加一个新的路由用于首页
@app.route('/')
def homepage():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)