import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(page_title="Shazam 集計ツール", layout="wide")
st.title("🎵 Shazam 日時別データ分析")

# 2. GoogleスプレッドシートからExcel形式（.xlsx）でデータを自動取得
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BO-Y5NS12H8ydqcWcICy6VH6iQrF6UqmdLxAL1e2Sn4/export?format=xlsx"

@st.cache_data(ttl=0)
def load_all_sheets():
    # Excelファイルを読み込み、全タブのデータを {タブ名: DataFrame} の辞書形式で一括キャッシュする
    xls = pd.ExcelFile(SHEET_URL)
    all_sheets = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # 1列目（日付）の列名を 'datetime' に変更し、日付型に変換
        if not df.empty:
            df.rename(columns={df.columns[0]: 'datetime'}, inplace=True)
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df = df.dropna(subset=['datetime'])
            all_sheets[sheet_name] = df
            
    return all_sheets

try:
    # 全シートのデータを辞書として取得
    sheets_dict = load_all_sheets()
    # 辞書のキー（タブ名）の一覧をアーティスト名として取得
    artist_list = list(sheets_dict.keys())

    if artist_list:
        # 3. 2段階のセレクトボックスを配置
        col_select1, col_select2 = st.columns(2)
        
        with col_select1:
            # 1段階目：アーティスト（タブ名）を選択
            selected_artist = st.selectbox("アーティストを選択してください：", artist_list)
            
        # 選択されたアーティスト（タブ）のデータを取得
        df = sheets_dict[selected_artist]

        # 2列目以降のヘッダー（曲名）の一覧を取得
        track_list = list(df.columns[1:])

        if track_list:
            with col_select2:
                # 2段階目：曲名を選択
                selected_track = st.selectbox("曲名を選択してください：", track_list)

            # 4. 選択された曲のデータを抽出して並び替え
            filtered_df = df[['datetime', selected_track]].dropna().sort_values('datetime')
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
            st.error("選択したタブ内に曲名が見つかりませんでした。2列目以降に曲名が並んでいるか確認してください。")
    else:
        st.error("スプレッドシートからタブ（アーティスト名）が読み込めませんでした。")

except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー内容: {e}")