import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EDINET_API_KEY")

# 直近の提出書類一覧を取る（日付は適当な平日に。土日は書類が少ない）
url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
params = {
    "date": "2026-10-02",  # 平日を指定。古すぎると取れないので直近に
    "type": 2,  # 2 = 提出書類一覧（メタデータ）
    "Subscription-Key": API_KEY,  # ← キーをクエリに付ける
}

res = requests.get(url, params=params)
data = res.json()

print("キー読めた?:", bool(API_KEY))
print("APIのStatusCode:", data.get("metadata", {}).get("status"))
print("メッセージ:", data.get("metadata", {}).get("message"))
print("取得件数:", len(data.get("results", [])))

# 先頭3件だけ、提出者名と書類種別を表示
for doc in data.get("results", [])[:3]:
    print(" -", doc.get("filerName"), "/", doc.get("docDescription"))
