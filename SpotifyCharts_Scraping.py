import os
import time
import glob
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

#一週間前の日付を取得
from datetime import datetime, timedelta


# .env ファイルの内容を読み込む
load_dotenv()

# カレントディレクトリの取得
current_dir = os.getcwd()
# 一時ダウンロードフォルダパスの設定
tmp_download_dir = f'{current_dir}\\tmpDownloads'
# 一時フォルダの作成
if not os.path.exists(tmp_download_dir):
    os.mkdir(tmp_download_dir)
# Chromeオプション設定でダウンロード先の変更
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": str(tmp_download_dir)}
options.add_experimental_option("prefs", prefs)

driver_path = f'{current_dir}\\chromedriver-win64\\chromedriver.exe'
chrome_service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=chrome_service, options=options)


#SpotifyChartsにログインする
def SpotifyChartsLogin():
    url = "https://charts.spotify.com/home"
    #サイトのリンク
    driver.get(url=url)
    ##################### ここからWeb要素の探索 #####################
    # コピーしたセレクタを文字列に格納
    selector = "#__next > div > div > main > div.Content-sc-1n5ckz4-0.jyvkLv > div > section.ChartsHomeHero__StyledSection-sc-1vcyx6n-0.bDiUTk > div > div > div.ChartsHomeHero__HeroContent-sc-1vcyx6n-3.hEhOFo > div > a"
    element = driver.find_element(By.CSS_SELECTOR, selector)
    #クリック
    element.click()
    #ログイン画面に移行、ログインする
    time.sleep(1)
    username_selector = "#login-username"
    password_selector = "#login-password"
    username_element = driver.find_element(By.CSS_SELECTOR, username_selector)
    password_element = driver.find_element(By.CSS_SELECTOR, password_selector)

    #.envからusernameとpasswordを取得
    username=os.getenv('SP_USERNAME')
    password=os.getenv('SP_PASSWORD')
    username_element.send_keys(username)
    password_element.send_keys(password)
    time.sleep(1)
    password_element.send_keys(Keys.RETURN)  # Enterキーを押してログイン

    time.sleep(3)



#SpotifyChartsからcsvをダウンロードする
def SpotifyChartsCSV(url: str):
    #サイトのリンク
    time.sleep(2)
    driver.get(url=url)
    time.sleep(2)
    ##################### ここからWeb要素の探索 #####################
    # コピーしたセレクタを文字列に格納
    selector = "#__next > div > div > main > div.Content-sc-1n5ckz4-0.jyvkLv > div:nth-child(3) > div > div > a > button"
    element = driver.find_element(By.CSS_SELECTOR, selector)

    try:
        # セレクターを指定
        selector = '#__next > div > div > main > div.Content-sc-1n5ckz4-0.jyvkLv > div:nth-child(3) > div > div > a > button'

        # セレクターがクリック可能になるまで待機
        element = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )

        # 要素をクリック
        element.click()

    except Exception as e:
        print(f"エラーが発生しました: {e}")


# SpotifyChartsCSV(url)
SpotifyChartsLogin()

def get_last_thursday():
    # 今日の日付を取得
    today = datetime.now()
    # 今日が何曜日かを取得 (0: 月曜日, 1: 火曜日, ..., 6: 日曜日)
    current_weekday = today.weekday()
    # 今日から最も近い木曜日までの日数を計算
    days_until_last_thursday = (current_weekday - 3) % 7
    # 直近の木曜日の日付を計算
    last_thursday = today - timedelta(days=days_until_last_thursday)
    return last_thursday

# 直近の木曜日を取得
last_thursday = get_last_thursday()

def weekly(num: int,current_date = get_last_thursday() - timedelta(55*7)):
    
    for i in range(num):
        url = f'https://charts.spotify.com/charts/view/regional-jp-weekly/{current_date.strftime("%Y-%m-%d")}'
        SpotifyChartsCSV(url)
        # 前の1週間
        current_date = current_date - timedelta(days=7)

def daily(num: int,current_date = datetime.now() - timedelta(days=2+483)):
    for i in range(num):
        url = f'https://charts.spotify.com/charts/view/regional-jp-daily/{current_date.strftime("%Y-%m-%d")}'
        SpotifyChartsCSV(url)
        # 前の1週間
        current_date = current_date - timedelta(days=1)

# 現在の日付 - 1を取得
# current_date = datetime.now()
# 1週間に合わせる
# current_date = current_date - timedelta(days=8)
weekly(48)

#閉じる
time.sleep(5)
print("ダウンロード完了")
driver.quit()