import sys
sys.stdout.reconfigure(encoding='utf-8')

import speech_recognition as sr
import schedule
import time
from datetime import datetime
import re
import matplotlib.pyplot as plt
import os
import requests
import json

LOG_FILE = "health_log.txt"

# 1 語音輸入與自動轉文字
def record_health_note():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nPlease start speaking and stay silent for 3 seconds after finishing")
        audio = recognizer.listen(source, phrase_time_limit=8)

    try:
        text = recognizer.recognize_google(audio, language="zh-TW")
        print("The result:", text)
        save_log(text)
        analyze_keywords(text)
    except Exception as e:
        print("Speech recognition failed. Please try again", e)

# 語音紀錄體重
def record_weight():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nPlease say your weight (例如：我今天體重 60.5 公斤)")
        audio = recognizer.listen(source, phrase_time_limit=6)

    try:
        text = recognizer.recognize_google(audio, language="zh-TW")
        print("Speech result:", text)

        # 從語音中找數字（60、60.5）
        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            weight = match.group(1)
            log_text = f"體重紀錄: {weight} 公斤"
            save_log(log_text)
            print(f"Weight recorded: {weight} 公斤")
        else:
            print("No weight number detected, please try again.")

    except Exception as e:
        print("Speech recognition failed. Please try again.", e)

# 2 儲存文字日誌
def save_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    print("Saved to health log")

# 3 關鍵字分析
def analyze_keywords(text):
    if re.search(r"(藥|藥物|吃藥)", text):
        print("Detected medicine record")
    elif re.search(r"(走路|散步|運動|爬樓梯)", text):
        print("Detected exercise record")
    elif re.search(r"(睡|休息)", text):
        print("Detected sleep record")
    elif re.search(r"(重|公斤|kg)", text):
        print("Detected weight record")
    else:
        print("General lifestyle record")

# 4 自動提醒功能
def remind_to_eat_breakfast():
    print("Reminder: time to eat breakfast")

def remind_to_eat_lunch():
    print("Reminder: time to eat lunch")

def remind_to_eat_dinner():
    print("Reminder: time to eat dinner")

def remind_to_take_medicine():
    print("Reminder: time to take medicine")

def remind_to_exercise():
    print("Reminder: remember to exercise today")

schedule.every().day.at("07:00").do(remind_to_eat_breakfast)
schedule.every().day.at("07:20").do(remind_to_take_medicine)
schedule.every().day.at("10:00").do(remind_to_exercise)
schedule.every().day.at("12:00").do(remind_to_eat_lunch)
schedule.every().day.at("12:20").do(remind_to_take_medicine)
schedule.every().day.at("16:00").do(remind_to_exercise)
schedule.every().day.at("18:00").do(remind_to_eat_dinner)
schedule.every().day.at("18:20").do(remind_to_take_medicine)

# 5 繪製運動時長柱狀圖
def show_statistics():
    if not os.path.exists(LOG_FILE):
        print("No log data found")
        return

    days = {}  # key: 日期, value: 當日總運動分鐘數

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            # 找包含運動行為的紀錄
            if "運動" in line or "走路" in line or "散步" in line or "爬樓梯" in line:

                # 取得日期
                date = line.split("]")[0][1:11]

                # 預設 0 分鐘
                minutes = 0

                # 抓出「xx 分鐘」
                match_min = re.search(r"(\d+)\s*分(鐘)?", line)
                if match_min:
                    minutes = int(match_min.group(1))

                # 抓出「xx 小時」
                match_hr = re.search(r"(\d+(\.\d+)?)\s*小時", line)
                if match_hr:
                    hours = float(match_hr.group(1))
                    minutes = int(hours * 60)

                # 累積同一天的運動時長
                days[date] = days.get(date, 0) + minutes

    if not days:
        print("No exercise data available")
        return

    # Plot
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.bar(days.keys(), days.values())
    plt.xlabel("Date")
    plt.ylabel("Exercise Duration (minutes)")
    plt.title("Daily Exercise Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# 體重折線圖
def show_weight_chart():
    if not os.path.exists(LOG_FILE):
        print("No log file found")
        return

    dates = []
    weights = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "體重紀錄" in line:
                # 取日期
                date = line.split("]")[0][1:11]

                # 抓出數字
                match = re.search(r"(\d+(\.\d+)?) 公斤", line)
                if match:
                    weight = float(match.group(1))
                    dates.append(date)
                    weights.append(weight)

    if not dates:
        print("No weight records found")
        return

    # 依日期排序
    combined = list(zip(dates, weights))
    combined.sort(key=lambda x: x[0])
    dates, weights = zip(*combined)

    plt.rcParams['font.family'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.plot(dates, weights, marker='o')
    plt.xlabel("Date")
    plt.ylabel("Weight (kg)")
    plt.title("Weight Trend Chart")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 自動摘要今日內容
def summarize_today():
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(LOG_FILE):
        print("No log file found")
        return

    exercise = 0
    medicine = 0
    sleep = 0
    weight_records = []
    general = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if today in line:
                text = line.strip().split("]")[1]

                if "運動" in text or "散步" in text or "走路" in text or "爬樓梯" in text:
                    exercise += 1
                elif "藥" in text:
                    medicine += 1
                elif "睡" in text or "休息" in text:
                    sleep += 1
                elif "體重紀錄" in text:
                    weight_records.append(text)
                else:
                    general.append(text)

    print("\nSummary for today")
    print("Exercise records:", exercise)
    print("Medicine records:", medicine)
    print("Sleep related records:", sleep)
    print("Weight records:")
    for w in weight_records:
        print("-", w)
    print("General notes:")
    for g in general:
        print("-", g)

# 指定日期搜尋
def search_by_date():
    date = input("Enter date (YYYY-MM-DD): ")

    if not os.path.exists(LOG_FILE):
        print("No log file found")
        return

    found = False

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(f"[{date}"):
                print(line.strip())
                found = True

    if not found:
        print("No records for this date")

# main
def main_menu():
    while True:
        print("\n==== Voice Guided Health Log ====")
        print("1. Add new voice record")
        print("2. Record weight by voice")
        print("3. View weight chart")
        print("4. View exercise statistics chart")
        print("5. Run reminder system")
        print("6. Summarize today")
        print("7. Search by date")
        print("8. Exit")

        choice = input("Select an option:")
        if choice == "1":
            record_health_note()
        elif choice == "2":
            record_weight()
        elif choice == "3":
            show_weight_chart()
        elif choice == "4":
            show_statistics()
        elif choice == "5":
            print("Reminder system running. Press Ctrl+C to stop.")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReminder system stopped")
        elif choice == "6":
            summarize_today()
        elif choice == "7":
            search_by_date()
        elif choice == "8":
            print("Goodbye")
            break
        else:
            print("Please enter a number between 1 and 8")

if __name__ == "__main__":
    main_menu()
