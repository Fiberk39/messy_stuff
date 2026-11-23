# main.py
from utils import *
import requests
import json
import time
import random


with open('cookie.txt', 'r', encoding='utf-8') as f:
    COOKIE = f.read()

path = 'database.db'
init_db(path)

def main():
    users_uid = get_all_undigged_users_uid(path)
    for uid in users_uid:
        init_db(path)
        print(f"正在处理 UID: {uid}")
        data = find_all_data(uid, COOKIE)
        for user in data:
            if user:
                add_user(path, user)
        mark_user_as_digged(path, uid)
        close_db()

if __name__ == '__main__':
    main()