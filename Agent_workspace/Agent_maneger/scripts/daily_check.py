#!/usr/bin/env python3
import os
import shutil
import glob
import re
from datetime import datetime

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_MGMT_DIR = os.path.join(os.path.dirname(BASE_DIR), "Task_Management")
ACTIVE_DIR = os.path.join(TASK_MGMT_DIR, "02_Active")
CLOCK_DIR = os.path.join(BASE_DIR, "クロック受付")

def check_overdue_tasks():
    """Activeタスクの期限チェック"""
    print("Checking overdue tasks...")
    today = datetime.now().date()
    
    tasks = glob.glob(os.path.join(ACTIVE_DIR, "*.txt"))
    overdue_tasks = []
    
    for task_path in tasks:
        with open(task_path, 'r') as f:
            content = f.read()
            # 期限: YYYY/MM/DD 形式を探す
            match = re.search(r'期限.*(\d{4}/\d{2}/\d{2})', content)
            if match:
                deadline_str = match.group(1)
                deadline = datetime.strptime(deadline_str, "%Y/%m/%d").date()
                if deadline < today:
                    overdue_tasks.append((os.path.basename(task_path), deadline_str))
    
    if overdue_tasks:
        print("\n[ALERT] Overdue Tasks:")
        for task, date in overdue_tasks:
            print(f"- {task} (Deadline: {date})")
    else:
        print("No overdue tasks found.")

def check_new_clock_files():
    """クロック受付の新規確認"""
    print("\nChecking clock files...")
    files = glob.glob(os.path.join(CLOCK_DIR, "*.txt"))
    # 更新日時が新しい順に3件表示
    files.sort(key=os.path.getmtime, reverse=True)
    
    print("Recent 3 reports:")
    for f in files[:3]:
        print(f"- {os.path.basename(f)}")

if __name__ == "__main__":
    check_overdue_tasks()
    check_new_clock_files()
