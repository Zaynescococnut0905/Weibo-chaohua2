import requests
import csv
import os
import re
from datetime import datetime
import pytz

# === 核心配置区 ===
API_URL = "https://huati.weibo.cn/aj/discovery/rank?cate_id=126011&page=1&topic_to_page=&from=&wm=&isvivo=false"
CSV_FILE_NAME = "game_character_top7.csv"

# 已经帮你把之前发给我的 Cookie 完美填入了
MY_COOKIE = "SUB=_2A25EOlqvDeRhGeFH7VsT9ybLyT-IHXVnFADnrDV6PUJbitAbLVmmkWtNerXwC4fEbcWBRLyOvfiXBljLND_6v-Kc"


def parse_chinese_number(text):
    """将带有中文字符的数字（如 '6万'、'179万'）转换为纯数字"""
    if not text:
        return 0
    match = re.search(r'([\d\.]+)(万|亿)?', str(text))
    if not match:
        return 0
    num = float(match.group(1))
    unit = match.group(2)
    if unit == '万':
        num *= 10000
    elif unit == '亿':
        num *= 100000000
    return int(num)


def fetch_top7_data():
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] 开始抓取游戏角色超话前7名...")

    # 叠满伪装
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://huati.weibo.cn/",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": MY_COOKIE
    }

    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        if res.status_code == 200:
            try:
                data = res.json()
                character_list = data.get('data', {}).get('list', [])

                if character_list:
                    top7 = character_list[:7]
                    save_to_csv(current_time, top7)
                else:
                    print("⚠️ 成功解析 JSON，但未找到 list 数据。")
            except Exception as e:
                print(f"❌ JSON 解析失败！报错: {e}")
                print(f"🕵️‍♂️ 微博实际返回的前200个字符是:\n{res.text[:200]}")
        else:
            print(f"❌ 请求失败，状态码: {res.status_code}")
    except Exception as e:
        print(f"❌ 发生网络请求错误: {e}")


def save_to_csv(time_str, character_list):
    file_exists = os.path.isfile(CSV_FILE_NAME)

    with open(CSV_FILE_NAME, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(['时间', '排名', '角色名', '今日互动', '粉丝数'])

        for index, char_data in enumerate(character_list):
            rank = index + 1
            name = char_data.get('display_name', '未知')
            fans_str = char_data.get('fans_count', '0')
            super_desc = char_data.get('super_desc', '')

            interact_match = re.search(r'([\d\.]+万?)今日互动', super_desc)
            if interact_match:
                interact_str = interact_match.group(1)
                interact_num = parse_chinese_number(interact_str)
            else:
                interact_num = 0

            fans_num = parse_chinese_number(fans_str)

            writer.writerow([time_str, rank, name, interact_num, fans_num])
            print(f"✅ Top {rank}: {name} | 互动: {interact_num} | 粉丝: {fans_num}")


if __name__ == '__main__':
    fetch_top7_data()