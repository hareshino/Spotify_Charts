# Discription
Spotify Charts( https://charts.spotify.com/home )というサイトとSpotify APIを利用して、
日間または週間のストリーミング数のランキング上位200の曲に関する情報(dancabilityなど)を取得するプログラム。

# .envの設定
CLIENT_ID = Spotify Developer Dashboardで取得したクライアントID

CLIENT_SECRET = 同様に取得したクライアントシークレット

SP_USERNAME = Spotifyアカウントのメール又はユーザーネーム

SP_PASSWORD = パスワード

# chromedriverの設定
スクレイピングの際に必要。Chrome for Testingを
 https://googlechromelabs.github.io/chrome-for-testing/ からダウンロードして所定の位置に置く。

# SpotifyCharts_Scraping.py
Spotify Chartsにログインし、指定した数だけCSVダウンロードボタンを押しまくる。

# APICalls.py
SpotifyCharts_Scraping.pyで保存したCSVファイルを読み込んで、APIか情報を取得して追加する。

# csvConcat.py
CSVファイルを結合して1つのファイルにする。
