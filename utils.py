# utils.py
import sqlite3
import requests
import json


def init_db(path: str):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""--sql
        CREATE TABLE IF NOT EXISTS relation (
            fan_uid INTEGER,
            follow_uid INTEGER,
            PRIMARY KEY (fan_uid, follow_uid)
        )
    """)

    cursor.execute("""--sql
        CREATE TABLE IF NOT EXISTS user_info (
            b_uid INTEGER PRIMARY KEY,
            username TEXT,
            fans_num INTEGER,
            follow_num INTEGER,
            likes INTEGER,
            views INTEGER,
            sign TEXT,
            digged BOOLEAN DEFAULT 0,
            data_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print('√ initialized successfully')

def get_user_info(uid, cookie):
    url_fans = f'https://api.bilibili.com/x/relation/fans?pn=1&ps=24&vmid={uid}'
    url_follows = f'https://api.bilibili.com/x/relation/followings?order=desc&order_type=&vmid={uid}'
    url_upstat = f'https://api.bilibili.com/x/space/upstat?mid={uid}'
    url_stat = f'https://api.bilibili.com/x/relation/stat?vmid={uid}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36",
        "Cookie": cookie
    }
    fans_res = requests.request(
        'get', url_fans,
        headers=headers
    )
    follows_res = requests.request(
        'get', url_follows,
        headers=headers
    )
    upstat_res = requests.request(
        'get', url_upstat,
        headers=headers
    )
    stat_res = requests.request(
        'get', url_stat,
        headers=headers
    )
    return fans_res, follows_res, upstat_res, stat_res

def add_user(path, data):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""--sql
        INSERT OR IGNORE INTO user_info (b_uid, username, fans_num, follow_num, likes, views, sign)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data['uid'], data['username'], data['fans'], data['follows'], data['likes'], data['views'], data['sign']))

    if 'following' in data:
        cursor.execute("""--sql
            INSERT OR IGNORE INTO relation (fan_uid, follow_uid)
            VALUES (?, ?)
        """, (data['uid'], data['following']))
    elif 'fan' in data:
        cursor.execute("""--sql
            INSERT OR IGNORE INTO relation (fan_uid, follow_uid)
            VALUES (?, ?)
        """, (data['fan'], data['uid']))
    else:
        print(f"Error: Missing 'following' or 'fan' key in data for user {data['uid']}")

    conn.commit()
    conn.close()

def find_all_data(uid, cookie):
    res = []
    def search(info, is_fan: bool):
        if 'data' not in info:
            res.append(0)
            return
        for i in info['data']['list']:
            print(f"正在获取用户 {i['uname']} 的信息...")
            f_info = get_user_info(i['mid'], cookie)
            f_stat = json.loads(f_info[3].content.decode())
            f_upstat = json.loads(f_info[2].content.decode())

            u_uid = i['mid']
            username = i['uname']
            sign = i['sign']
            views = f_upstat['data']['archive']['view']
            likes = f_upstat['data']['likes']
            follows = f_stat['data']['following']
            fans = f_stat['data']['follower']

            if is_fan:
                res.append({
                    'uid': u_uid,
                    'username': username,
                    'sign': sign,
                    'views': views,
                    'likes': likes,
                    'follows': follows,
                    'fans': fans,
                    'following': uid
                })
            else:
                res.append({
                    'uid': u_uid,
                    'username': username,
                    'sign': sign,
                    'views': views,
                    'likes': likes,
                    'follows': follows,
                    'fans': fans,
                    'fan': uid
                })
    
    fan_info = get_user_info(uid, cookie)[0].content.decode()
    fan_info = json.loads(fan_info)
    search(fan_info, True)

    follow_info = get_user_info(uid, cookie)[1].content.decode()
    follow_info = json.loads(follow_info)
    search(follow_info, False)
    return res

def get_all_undigged_users_uid(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""--sql
        SELECT b_uid FROM user_info WHERE digged = 0
    """)
    undigged_users = cursor.fetchall()
    undigged_users = [user[0] for user in undigged_users]

    conn.close()
    return undigged_users

def mark_user_as_digged(path, uid):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""--sql
        UPDATE user_info SET digged = 1 WHERE b_uid = ?
    """, (uid,))

    conn.commit()
    conn.close()