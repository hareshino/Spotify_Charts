import pandas as pd
from datetime import datetime, timedelta

def concatCSV(df1,df2):
    #結合
    result = pd.concat([df1, df2], ignore_index=True)

    return result

result = pd.DataFrame()

def get_last_thursday_in_past():
    # 今日の日付を取得
    today = datetime.now()

    # 今日が何曜日かを取得 (0: 月曜日, 1: 火曜日, ..., 6: 日曜日)
    current_weekday = today.weekday()

    # 今日から最も近い過去の木曜日までの日数を計算
    days_until_last_thursday = (current_weekday - 3) % 7

    # 直近の木曜日の日付を計算
    last_thursday = today - timedelta(days=days_until_last_thursday)

    return last_thursday

# 過去の直近の木曜日を取得
date = get_last_thursday_in_past()
date = date - timedelta(51*7)
for i in range(54):
    path=f'./data_analysis/spotify_top200_jp_weeks_{date.strftime("%Y-%m-%d")}.csv'
    df = pd.read_csv(path)
    result = concatCSV(result,df)
    next = 7
    date = date - timedelta(next)

result.to_csv("result.csv",index=False,encoding="utf-8-sig")