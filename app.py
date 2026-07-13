import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam 日時別データ分析")

# 2. Googleスプレッドシートからデータを自動取得
# ※ YOUR_SHEET_ID の部分はご自身のスプレッドシートのIDに書き換えてください
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4/export?format=csv"

@st.cache_data(ttl=0) # データをキャッシュせず毎回最新版を読み込む
def load_data():
    # 列数が合わないエラー行を自動で飛ばす
    df = pd.read_csv(SHEET_URL, on_bad_lines='skip')
    
    # ➔ 【超重要：修正箇所】1列目（日付）の列名だけをピンポイントで 'datetime' に変更
    df.rename(columns={df.columns[0]: 'datetime'}, inplace=True)
    
    # 日付と時間を自動判定して変換（エラーになる行は無効化）
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    
    # 日付になれなかった行を完全に削除して、列のデータ型を「日付型」に確定させる
    df = df.dropna(subset=['datetime'])
    return df

try:
    df = load_data()

    # 3. 2列目以降のヘッダー（曲名）の一覧をスプレッドシートの並び順のまま取得
    track_list = list(df.columns[1:])
    
    if track_list:
        selected_track = st.selectbox("分析したい曲名を選択してください：", track_list)

        # 4. 選択された曲のデータ（日時と対象曲の列）を抽出して並び替え
        filtered_df = df[['datetime', selected_track]].dropna().sort_values('datetime')
        
        # グラフ表示用に列名を分かりやすく変更
        filtered_df = filtered_df.rename(columns={selected_track: 'shazams'})

        if not filtered_df.empty:
            # 5. レイアウト（左右2カラムに分割）
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Shazam数の推移")
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
        st.error("スプレッドシートから曲名が読み込めませんでした。2列目以降に曲名が正しく並んでいるか確認してください。")

except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー内容: {e}")
