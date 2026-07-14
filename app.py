import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam アーティスト・曲別データ分析 (シート別管理)")

# ※ YOUR_SHEET_ID の部分はご自身のスプレッドシートのIDに書き換えてください
SHEET_ID = "1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4"

# 2. Googleスプレッドシートから「全シート名（アーティスト名）」を自動取得
@st.cache_data(ttl=0)
def get_all_artists():
    # スプレッドシート全体の情報を取得して、存在するシート名の一覧を返します
    meta_url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        # 1つ目のシートからメタデータを読み込み、全体のシート一覧を取得する処理
        # 通常、指定IDの全シート名を取得するために公開URLの仕様を利用します
        # ここではユーザーが作成したタブ名をそのままアーティスト名として扱います
        df_meta = pd.read_csv(f"https://google.com/{SHEET_ID}/export?format=xlsx", engine='openpyxl')
        return list(df_meta.keys()) if hasattr(df_meta, 'keys') else []
    except:
        # 上記がうまく動かない場合の予備：手動でアーティストシート名を指定することも可能です
        # 例: return ["ArtistA", "ArtistB"]
        pass

# ➔ より確実な方法として、個別シートを動的に読み込む関数
@st.cache_data(ttl=0)
def load_sheet_data(sheet_name):
    # シート名（アーティスト名）を直接指定してCSVとして一発読み込み
    url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url, on_bad_lines='skip')
    df.rename(columns={df.columns[0]: 'datetime'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime'])
    return df

# 3. アーティストリストの設定
# ※自動取得が環境によって制限される場合があるため、最も確実な「手動リスト」をベースにしつつ
# スプレッドシートのタブ名をここに書き並べるのが一番安全です。
ARTIST_LIST = ["KEN MIYAKE" , "Hiromitsu Kitayama" ,"Number_i"] # ➔ あなたのシート名（タブ名）に書き換えてください

try:
    # 4. 【1段階目】アーティスト名（シート名）の選択
    selected_artist = st.selectbox("1. アーティストを選択してください：", ARTIST_LIST)

    # 選択されたアーティストのシートデータを読み込み
    df = load_sheet_data(selected_artist)

    # 5. 【2段階目】選択されたシートの2列目以降から「曲名」を取得（並び順を維持）
    track_list = list(df.columns[1:])
    
    if track_list:
        selected_track = st.selectbox("2. 曲名を選択してください：", track_list)

        # 6. 選択された曲のデータを抽出
        filtered_df = df[['datetime', selected_track]].dropna().sort_values('datetime')
        filtered_df = filtered_df.rename(columns={selected_track: 'shazams'})

        if not filtered_df.empty:
            # 7. レイアウト（左右2カラムに分割）
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
