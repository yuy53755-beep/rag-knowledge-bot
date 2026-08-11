import requests
import math
from dotenv import load_dotenv
import os

load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
KIMI_API_KEY = os.getenv("KIMI_API_KEY")

# ----------------------工具函数1：调用通义获取向量----------------------
def get_embedding(text: str):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "text-embedding-v2",
        "input": text
    }
    resp = requests.post(url, headers=headers, json=payload)
    res_json = resp.json()
    return res_json["data"][0]["embedding"]

# ----------------------工具函数2：余弦相似度计算----------------------
def cosine_similarity(vec_a, vec_b):
    dot = sum(a*b for a,b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(x*x for x in vec_a))
    norm_b = math.sqrt(sum(x*x for x in vec_b))
    if norm_a == 0 or norm_b ==0:
        return 0.0
    return dot/(norm_a*norm_b)

# ----------------------1、准备知识库----------------------
knowledge = [
    "RAG全称检索增强生成，分为检索和生成两个阶段。",
    "检索阶段：把文档切成小块，转为向量，用户问题向量化后做相似度匹配，拿到相关片段。",
    "生成阶段：把检索出来的参考片段连同用户问题一起交给大模型，大模型依据参考资料输出答案。",
    "RAG不会改变大模型本身，只是‘现场翻参考书给模型看'",
    "access_token是登录之后后端颁发的凭证，放在请求头Authorization: Bearer tokenValue做身份校验。"
]

# 对知识库全部向量化
kb_embeds = []
for doc in knowledge:
    vec = get_embedding(doc)
    kb_embeds.append({"text":doc, "vec":vec})

# ----------------------2、用户提问，召回top1相关文档----------------------
# user_query = "什么是access_token？"
user_query="什么是RAG？"
query_vec = get_embedding(user_query)

# 算相似度排序
for item in kb_embeds:
    item["score"] = cosine_similarity(query_vec, item["vec"])
# kb_embeds.sort(key=lambda x:x["score"], reverse=True)
# top_context = kb_embeds[0]["text"]

# print(f"\n【召回的参考文档】score={kb_embeds[0]['score']:.4f}")
# print(top_context)

# 排序之后，不要只拿第0个，取前3条
kb_embeds.sort(key=lambda x:x["score"], reverse=True)
# top‑3召回，拼接多条上下文
top_context_list = kb_embeds[:3]
top_context = "\n".join([item["text"] for item in top_context_list])

print(f"\n【召回的参考文档条数：{len(top_context_list)}】")
for idx,item in enumerate(top_context_list):
    print(f"score={item['score']:.4f}  {idx+1}. {item['text']}")

# ----------------------3、把上下文交给Kimi大模型生成答案----------------------
prompt = f"""参考下面资料回答用户问题，如果资料没有相关信息就如实说不知道。
参考资料：
{top_context}

用户问题：{user_query}
"""

chat_url = "https://api.moonshot.cn/v1/chat/completions"
chat_headers = {
    "Authorization": f"Bearer {KIMI_API_KEY}",
    "Content-Type":"application/json"
}
chat_payload = {
    "model":"kimi-k3",
    "messages":[{"role":"user","content":prompt}],
    "temperature":1
}

chat_resp = requests.post(chat_url, headers=chat_headers, json=chat_payload)
chat_result = chat_resp.json()
answer = chat_result["choices"][0]["message"]["content"]

print("\n【大模型RAG回答】")
print(answer)
