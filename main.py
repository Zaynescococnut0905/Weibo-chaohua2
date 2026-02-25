import requests
import csv
import os
import re
from datetime import datetime
import pytz

# === 核心配置区 (从 GitHub Secrets 获取安全凭证) ===
# ⚠️ 必须在 GitHub 仓库的 Settings -> Secrets 中添加这三个变量
API_URL = os.environ.get("WEIBO_APP_URL", "")
AUTH_TOKEN = os.environ.get("WEIBO_AUTH", "")
SESSION_ID = os.environ.get("WEIBO_SESSION", "")

CSV_FILE_NAME = "game_character_top7.csv"

def parse_num(text):
    """提取字符串中的纯数字"""
    if not text: return 0
    match = re.search(r'([\d\.]+)(万|亿)?', str(text))
    if not match: return 0
    num = float(match.group(1))
    unit = match.group(2)
    if unit == '万': num *= 10000
    elif unit == '亿': num *= 100000000
    return int(num)

def fetch_top7_data():
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    if not API_URL or not AUTH_TOKEN:
        print("❌ 错误：GitHub Secrets 中未配置 API_URL 或 AUTH_TOKEN")
        return

    print(f"[{current_time}] 正在通过 App 接口抓取精准热度数据...")

    headers = {
        "Host": "api.weibo.cn",
        "User-Agent": "Weibo/98241 (iPhone; iOS 26.2.1; Scale/3.00)",
        "Authorization": AUTH_TOKEN,
        "X-Sessionid": SESSION_ID,
        "Accept-Language": "ja,en-US,en"
    }

    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            char_list = data.get('content', {}).get('list', [])
            if char_list:
                save_to_csv(current_time, char_list[:7])
                print(f"✅ 数据抓取成功并存入 {CSV_FILE_NAME}")
            else:
                print("⚠️ 未找到角色列表，请检查接口返回结构")
        else:
            print(f"❌ 请求失败，状态码: {res.status_code}")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

def save_to_csv(time_str, items):
    file_exists = os.path.isfile(CSV_FILE_NAME)
    with open(CSV_FILE_NAME, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['时间', '排名', '角色名', '热度值', '粉丝数'])
        
        for index, item in enumerate(items):
            rank = index + 1
            # 提取名字
            name_info = item.get('title', [{}])[0].get('content', '未知')
            # 提取热度与粉丝 (如: "84457热度 179万小狸花")
            sub_info = item.get('sub_title', [{}])[0].get('content', '')
            
            heat_val = 0
            fans_num = 0
            
            heat_match = re.search(r'(\d+)热度', sub_info)
            if heat_match: heat_val = int(heat_match.group(1))
            
            fans_match = re.search(r'([\d\.]+万)', sub_info)
            if fans_match: fans_num = parse_num(fans_match.group(1))

            writer.writerow([time_str, rank, name_info, heat_val, fans_num])
            print(f"✅ Top {rank}: {name_info} | 热度: {heat_val}")

if __name__ == '__main__':
    fetch_top7_data()
