import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
# .envファイルの内容を読み込見込む
load_dotenv()

# Spotify Developer Dashboardで取得したクライアントIDとクライアントシークレット
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

# 認証用のエンドポイント
auth_url = 'https://accounts.spotify.com/api/token'

# 認証用の情報を作成
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}

# アクセストークンを取得
auth_response = requests.post(auth_url, data=auth_data)
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

def get_audio_features(track_id, access_token):
    endpoint = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    retries=10
    sleep_time=1

    for _ in range(retries):
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                audio_features = response.json()
                return audio_features
            elif response.status_code == 429:
                print("API rate limit exceeded. Retrying after sleeping.(audio-features)")
                time.sleep(sleep_time)
            else:
                print(f"エラー: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

import requests

def get_track_genres(track_id, access_token):
    endpoint = f'https://api.spotify.com/v1/tracks/{track_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    retries=10
    sleep_time=1

    for _ in range(retries):
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                track_info = response.json()
                artist_id = track_info['artists'][0]['id']
            elif response.status_code == 429:
                print("API rate limit exceeded. Retrying after sleeping.(track-id)")
                time.sleep(sleep_time)
            else:
                print(f"エラー: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    # アーティストの詳細情報を取得
    endpoint = f'https://api.spotify.com/v1/artists/{artist_id}'
    response = requests.get(endpoint, headers=headers)
    for _ in range(retries):
        try:
            if response.status_code == 200:
                artist_data = response.json()
                genres = artist_data['genres']
                return genres
            elif response.status_code == 429:
                print("API rate limit exceeded. Retrying after sleeping.(artist-id)")
                time.sleep(sleep_time)
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

# トラックIDとアクセストークンを指定(要取得！)
# access_token = ''

def getInfo(current_date: datetime):

    dfsongs = pd.read_csv(f'./Weekly_2023/regional-jp-weekly-{current_date.strftime("%Y-%m-%d")}.csv',encoding='utf-8-sig')

    song_info = []

    # 'uri'行だけを取り出す
    uri = dfsongs.iloc[:,1]
    remove = "spotify:track:"

    i=0
    for url in uri:
        id = url.replace(remove,"")
        data = get_audio_features(id, access_token)
        genre = get_track_genres(id, access_token)
        #genre追加
        print(i)
        i = i + 1
        data['artist_genre'] = genre
        data['date'] = current_date.strftime("%Y-%m-%d") #日付を追加 2023-11-23なら2023-11-17から2023-11-23までのデータ
        song_info.append(data)
    dfinfo = pd.DataFrame(song_info)

    dfinfo.to_csv('apiData.csv',index=True, encoding='utf_8-sig')

    # 'ID'列をキーにして結合
    merged_df = pd.concat([dfsongs,dfinfo],axis=1)

    # 分析に不要な列を削除
    merged_df = merged_df.drop(columns=['uri'])
    df_analysis = merged_df.drop(columns=['id','analysis_url','track_href'])

    #保存
    csv_file_path = f'./data/weeks_{date.strftime("%Y-%m-%d")}.csv'
    merged_df.to_csv(csv_file_path, index=True, encoding='utf_8-sig')

    csv_file_path = f'./data_analysis/spotify_top200_jp_weeks_{date.strftime("%Y-%m-%d")}.csv'
    df_analysis.to_csv(csv_file_path, index=True, encoding='utf_8-sig')
    
date = datetime.now() - timedelta(22)
for i in range(102):
    print(f'取得開始:{date.strftime("%Y-%m-%d")}')
    getInfo(date)
    date = date - timedelta(7)
    print(f'取得完了:{date.strftime("%Y-%m-%d")}')
    time.sleep(1)
