import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam 日時別データ分析")

# 2. Googleスプレッドシートからデータを自動取得
# ※ YOUR_SHEET_ID の部分はご自身のスプレッドシートのIDに書き換えてください
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4/export?format=csv"

@st.cache_data(ttl=600) # 10分間データをキャッシュして高速化
def load_data():
    df = pd.read_csv(SHEET_URL)
    # 1列目の名前が何であっても 'datetime' に統一する
    df.columns.values[0] = 'datetime'
    # 日付と時間を自動判定して変換（エラーになる行は無効化）
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    return df

try:
    df = load_data()
    # on_bad_lines='skip' を追加し、列数が合わないエラー行（4行目など）を自動で飛ばします
    df = pd.read_csv(SHEET_URL, on_bad_lines='skip')

    # 3. 2列目以降のヘッダー（曲名）の一覧を取得してソート
    track_list = sorted(list(df.columns[1:]))
    selected_track = st.selectbox("分析したい曲名を選択してください：", track_list)

    # 4. 選択された曲のデータ（日時と対象曲の列）を抽出して並び替え
    filtered_df = df[['datetime', selected_track]].dropna().sort_values('datetime')
    
    # グラフ表示用に列名を分かりやすく変更
    filtered_df = filtered_df.rename(columns={selected_track: 'shazams'})

    if not filtered_df.empty:
        # 5. レイアウト（左右2カラムに分割）
        col1, col2 = st.columns()

        with col1:
            st.subheader("📈 Shazam数の推移")
            # グラフのX軸を時間単位まで細かく表示
            fig = px.line(filtered_df, x='datetime', y='shazams', 
                          labels={'datetime': '日時', 'shazams': 'Shazam数'},
                          markers=True)
            # マウスを乗せたときに「○年○月○日 ○時」と出るようにフォーマット指定
            fig.update_traces(hovertemplate='日時: %{x|%Y-%m-%d %H:%M}<br>Shazam数: %{y}')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 データ一覧")
            # 表データも見やすい「年-月-日 時:分」の形式に整えて表示
            display_df = filtered_df.copy()
            display_df['datetime'] = display_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df, height=400, use_container_width=True)
    else:
        st.warning("選択された曲のデータが見つかりませんでした。")

except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー内容: {e}")
