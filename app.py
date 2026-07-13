import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam 日別データ分析")

# 2. Googleスプレッドシートからデータを自動取得
# ※ YOUR_SHEET_ID の部分はご自身のスプレッドシートのIDに書き換えてください
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4"

@st.cache_data(ttl=600) # 10分間データをキャッシュして高速化
def load_data():
    df = pd.read_csv(SHEET_URL)
    # 1列目の名前が何であっても 'date' に統一する
    df.columns.values[0] = 'date'
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()

    # 3. 2列目以降のヘッダー（曲名）の一覧を取得してソート
    track_list = sorted(list(df.columns[1:]))
    selected_track = st.selectbox("分析したい曲名を選択してください：", track_list)

    # 4. 選択された曲のデータ（日付と対象曲の列）を抽出して並び替え
    filtered_df = df[['date', selected_track]].dropna().sort_values('date')
    
    # グラフ表示用に列名を分かりやすく変更
    filtered_df = filtered_df.rename(columns={selected_track: 'shazams'})

    if not filtered_df.empty:
        # 5. レイアウト（左右2カラムに分割）
        col1, col2 = st.columns()

        with col1:
            st.subheader("📈 Shazam数の推移")
            fig = px.line(filtered_df, x='date', y='shazams', 
                          labels={'date': '日付', 'shazams': 'Shazam数'},
                          markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 データ一覧")
            # 見やすい日付形式に整えて表示
            display_df = filtered_df.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, height=400, use_container_width=True)
    else:
        st.warning("選択された曲のデータが見つかりませんでした。")

except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー内容: {e}")
