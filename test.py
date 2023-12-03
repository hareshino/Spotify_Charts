import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
# .envファイルの内容を読み込む
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

def get_access_token(client_id,client_secret):
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }    
    auth_response = requests.post(auth_url, data=auth_data)
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']

    return access_token


def get_audio_features(track_id, access_token):
    endpoint = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    retries=20
    sleep_time=10

    for _ in range(retries):
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                audio_features = response.json()
                return audio_features
            elif response.status_code == 429:
                print("API rate limit exceeded. Retrying after sleeping.(audio-features)")
                time.sleep(sleep_time)
            elif response.status_code == 401:
                auth_response = requests.post(auth_url, data=auth_data)
                auth_response_data = auth_response.json()
                access_token = auth_response_data['access_token']
            else:
                print(f"エラー: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

def get_track_genres(track_id, access_token):
    endpoint = f'https://api.spotify.com/v1/tracks/{track_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    #retries:試行回数,sleep_time:429の時の待機時間,i:429が一定回数のときclient_idを変える
    retries=20
    sleep_time=10

    for _ in range(retries):
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                track_info = response.json()
                artist_id = track_info['artists'][0]['id']
            elif response.status_code == 429:
                print("API rate limit exceeded. Retrying after sleeping.(track-id)")
                time.sleep(sleep_time)
            elif response.status_code == 401:
                auth_response = requests.post(auth_url, data=auth_data)
                auth_response_data = auth_response.json()
                access_token = auth_response_data['access_token']
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
            elif response.status_code == 401:
                auth_response = requests.post(auth_url, data=auth_data)
                auth_response_data = auth_response.json()
                access_token = auth_response_data['access_token']
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

cache = pd.DataFrame()  # 重複してAPIから取ってくることを避けるためのDataFrame
date = datetime.now() - timedelta(9)
cache = pd.read_csv(f'./data/weeks_{date.strftime("%Y-%m-%d")}.csv', index_col=None)
for i in range(34):
    date = date - timedelta(7)
    cache2 = pd.read_csv(f'./data/weeks_{date.strftime("%Y-%m-%d")}.csv', index_col=None)
    cache = pd.concat([cache,cache2],ignore_index=True)
date = datetime.now() - timedelta(9)

def getInfo(current_date: datetime, cache):

    dfsongs = pd.read_csv(f'./Weekly_2023/regional-jp-weekly-{current_date.strftime("%Y-%m-%d")}.csv',encoding='utf-8-sig',index_col=None)

    song_info = []

    # 'uri'行だけを取り出す
    uri = dfsongs.iloc[:,1]
    remove = "spotify:track:"

    i=0
    for url in uri:
        print(i)
        i = i + 1
        #trackのuriの文字列からid部分を抜き出す
        id = url.replace(remove,"")
        #キャッシュに既にある場合
        if id in cache['id'].values:
            # IDに対する行を取得
            row = cache[cache['id'] == id].iloc[0]
            # 列名を取得して、すべての列に対する情報を辞書に追加
            data = {col: row[col] for col in cache.columns if col not in ['date', 'rank', 'artist_names', 'track_name', 'source', 'peak_rank', 'previous_rank', 'weeks_on_chart', 'streams']}
            #日付を追加 2023-11-23なら2023-11-17から2023-11-23までのデータ
            data['date'] = current_date.strftime("%Y-%m-%d")
            print(f'重複!{i}')
        #まだAPIから取ってきてない場合
        else:
            data = get_audio_features(id, access_token)
            time.sleep(1)
            genre = get_track_genres(id, access_token)
            #genre追加
            data['artist_genre'] = genre
            #日付を追加 2023-11-23なら2023-11-17から2023-11-23までのデータ
            data['date'] = current_date.strftime("%Y-%m-%d")
            print("API取得!")

        #listに追加
        song_info.append(data)
    dfinfo = pd.DataFrame(song_info)

    dfinfo.to_csv('apiData.csv',index=False, encoding='utf_8-sig')

    # 'ID'列をキーにして結合
    merged_df = pd.concat([dfsongs,dfinfo],axis=1)

    # 分析に不要な列を削除
    if 'Unnamed: 0' in merged_df.columns:
        merged_df = merged_df.drop(columns=['Unnamed: 0'])
    merged_df = merged_df.drop(columns=['uri'])
    df_analysis = merged_df.drop(columns=['id','analysis_url','track_href'])

    #保存
    csv_file_path = f'./data/weeks_{date.strftime("%Y-%m-%d")}.csv'
    merged_df.to_csv(csv_file_path, index=False, encoding='utf_8-sig')

    csv_file_path = f'./data_analysis/spotify_top200_jp_weeks_{date.strftime("%Y-%m-%d")}.csv'
    df_analysis.to_csv(csv_file_path, index=False, encoding='utf_8-sig')

    return merged_df

date = datetime.now() - timedelta(2)

for i in range(2):
    print(f'取得開始:{(date + timedelta(7)).strftime("%Y-%m-%d")}')
    #CSVに取得データを書き込むとともに、重複を避けるためにキャッシュに保存
    tmp = getInfo(date,cache)
    cache = pd.concat([cache,tmp],ignore_index=True)
    #次の一週間
    print(f'取得完了:{(date + timedelta(7)).strftime("%Y-%m-%d")}')
    date = date - timedelta(7)
    # time.sleep(0.4)
