import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
import re

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam アーティスト・曲別データ分析 (シート別管理)")

# ==============================================================
# ⚠️ ここにスプレッドシートの「URL全体」をそのまま貼り付けてください！
# 例: SHEET_URL = "https://google.com"
# ==============================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4"

# 2. 個別シートを安全に読み込む関数
@st.cache_data(ttl=0)
def load_sheet_data(sheet_name):
    # ➔ URL全体から「ID（英数字の塊）」の部分だけを自動で抜き出すガード処理
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", SHEET_URL.strip())
    if not match:
        st.error("スプレッドシートのURLが正しくありません。URL全体が貼り付けられているか確認してください。")
        st.stop()
    
    clean_id = match.group(1)
    
    # シート名（空白入りなど）をインターネット用の正しい通信文字に安全に変換
    safe_sheet_name = urllib.parse.quote(sheet_name)
    
    # ➔ 【最重要】ネットワークエラーを回避する最新の安全なエクスポートURL形式
    url = f"https://docs.google.com{clean_id}/export?format=csv&sheet={safe_sheet_name}"
    
    # データを読み込み
    df = pd.read_csv(url, on_bad_lines='skip')
    
    # 1列目を確実に日時列として処理する
    df.rename(columns={df.columns[0]: 'datetime'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime'])
    return df

# ==============================================================
# ⚠️ 注意: ここにあなたの「実際のGoogleスプレッドシートのタブ名」を正確に入力してください
# ==============================================================
ARTIST_LIST = ["KenMiyake", "Hiromitsu Kitayama", "Number_i"] 

try:
    # 3. 【1段階目】アーティスト名（シート名）の選択
    selected_artist = st.selectbox("1. アーティストを選択してください：", ARTIST_LIST)

    # 選択されたアーティストのシートデータを読み込み
    df = load_sheet_data(selected_artist)

    # 4. 【2段階目】選択されたシートの2列目以降から「曲名」を取得（並び順を維持）
    track_list = list(df.columns[1:])
    
    if track_list:
        selected_track = st.selectbox("2. 曲名を選択してください：", track_list)

        # 5. 選択された曲のデータを抽出
        filtered_df = df[['datetime', selected_track]].dropna().sort_values('datetime')
        filtered_df = filtered_df.rename(columns={selected_track: 'shazams'})

        if not filtered_df.empty:
            # 6. レイアウト（左右2カラムに分割）
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"📈 {selected_artist} - {selected_track} の推移")
                fig = px.line(filtered_df, x='datetime', y='shazams', 
                              labels={'datetime': '日時', 'shazams': 'Shazam数'},
                              markers=True)
                fig.update_traces(hovertemplate='日時: %{x|%Y-%m-%d %H:%M}<br>Shazam数: %{y}')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📊 データ一覧")
                display_df = filtered_df.copy()
                display_df['datetime'] = display_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(display_df, height=400, use_container_width=True)
        else:
            st.warning("選択された曲のデータが見つかりませんでした。")
    else:
        st.error("シートから曲名が読み込めませんでした。2列目以降に曲名が並んでいるか確認してください。")

except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー内容: {e}")
