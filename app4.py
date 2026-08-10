from flask import Flask, jsonify, request

app = Flask(__name__)

# 模拟数据库保存用户账号密码 【改名，避免和函数重名】
user_db = {
    "username": "testuser",
    "password": "123456"
}

# 模拟token存储，实际项目放redis
mock_token = None

# 登录接口：账号密码换取access_token
@app.route("/login/access_token", methods=["POST"])
def login():
    global mock_token
    data = request.get_json()
    # 处理没有json体的情况，防止500
    if not data:
        return jsonify({"code":400, "msg":"请求体必须是JSON格式"}), 400

    username = data.get("username")
    password = data.get("password")

    if username == user_db["username"] and password == user_db["password"]:
        mock_token = "abcdef123456-mytoken-001" # 全部英文半角符号
        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "access_token": mock_token
        })
    else:
        return jsonify({"code":401, "msg":"账号密码错误"}),401

# 需要token才能访问的受保护接口
@app.route("/user/info", methods=["GET"])
def user_info():
    auth_header = request.headers.get("Authorization")
    # Bearer 规范格式：Authorization: Bearer abcdef123456‑mytoken‑001
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"code":401,"msg":"token无效，请重新登录"}),401

    token = auth_header[7:]
    if token != mock_token:
        return jsonify({"code":401,"msg":"token无效，请重新登录"}),401

    return jsonify({
        "code":200,
        "data":{"username":"testuser","desc":"这是受token保护返回的用户数据"}
    })


if __name__ == "__main__":
    # 监听本机5000端口
    app.run(host="127.0.0.1", port=5000, debug=True)