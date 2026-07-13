import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title(" Shazam 日別データ分析")

# 2. Googleスプレッドシートからデータを自動取得
# ※「/edit#gid=0」の部分を「/export?format=csv」に置き換えてCSVとして読み込みます
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4/export?format=csv"

@st.cache_data(ttl=600) # 10分間データをキャッシュして高速化
def load_data():
    df = pd.read_csv(SHEET_URL)
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()

    # 3. 曲名選択のプルダウン（重複を除外してソート）
    track_list = sorted(df['track_name'].dropna().unique())
    selected_track = st.selectbox("分析したい曲名を選択してください：", track_list)

    # 4. 選択された曲のデータを抽出
    filtered_df = df[df['track_name'] == selected_track].sort_values('date')

    if not filtered_df.empty:
        # 5. レイアウト（左右2カラムに分割）
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📈 Shazam数の推移")
            fig = px.line(filtered_df, x='date', y='shazams', 
                          labels={'date': '日付', 'shazams': 'Shazam数'},
                          markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 データ一覧")
            # 見やすい形式に整えて表示
            display_df = filtered_df[['date', 'shazams']].copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, height=400, use_container_width=True)
    else:
        st.warning("選択された曲のデータが見つかりませんでした。")

except Exception as e:
    st.error("データの読み込みに失敗しました。スプレッドシートのURLや列名を確認してください。")
