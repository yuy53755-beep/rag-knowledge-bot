from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("DEEPSEEK_API_KEY")
if key:
    print(f"读取成功，密钥前缀：{key[:10]}")
else:
    print("未读到API密钥，请检查.env")
