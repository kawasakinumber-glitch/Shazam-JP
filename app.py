import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam 曲別データ分析")

# ==============================================================
# ⚠️ 注意: ここにURLではなく、長〜い英数字の「IDだけ」を正確に入れてください！
# ==============================================================
SHEET_ID = "1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4"

# 2. 毎回リアルタイムにデータを読み込む関数
@st.cache_data(ttl=0) # ➔ ttl=0 でキャッシュを無効化し、常に最新の数値を読み込みます
def load_data():
    # IDの前後にあるスペースや改行を自動で完全消去
    clean_id = SHEET_ID.strip().replace(' ', '').replace('\n', '').replace('\r', '')
    
    # ://google.com を使った正しいCSVエクスポート形式です（1枚目のシートが読み込まれます）
    url = f"https://://google.com/spreadsheets/d/{clean_id}/export?format=csv"
    
    # データを読み込み
    df = pd.read_csv(url, on_bad_lines='skip')
    
    # 1列目を確実に日時列として処理する
    df.rename(columns={df.columns[0]: 'datetime'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime'])
    return df

try:
    df = load_data()

    # 3. 2列目以降のヘッダー（曲名）の一覧を取得（並び順を維持）
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
                st.subheader(f"📈 {selected_track} の推移")
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
        st.error("スプレッドシートから曲名が読み込めませんでした。2列目以降に曲名が並んでいるか確認してください。")

except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー内容: {e}")