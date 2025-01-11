import streamlit as st
import pandas as pd
import glob

# 📂 CSVファイルが保存されているフォルダ
csv_folder = "data/"

# 📂 フォルダ内のすべてのCSVファイルを取得
csv_files = glob.glob(csv_folder + "*.csv")

# 📊 CSVファイルをすべて結合
df_list = [pd.read_csv(file, encoding="utf-8-sig") for file in csv_files]
df = pd.concat(df_list, ignore_index=True)

# 🔍 データクリーニング (カラム名の種類チェック)
df.rename(columns={"アイテム": "加工品"}, inplace=True)

# ⏳ 日時データを適切に整形
df["日時"] = pd.to_datetime(df["日時"])
df = df.sort_values("日時")

# 🎧 Streamlit UI
st.title("チームともだち♡倉庫履歴🫶")

# 📀 開始日 & 終了日を選択
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 開始日", df["日時"].min().date())
with col2:
    end_date = st.date_input("📅 終了日", df["日時"].max().date())

# 🔍 効果の検索フィルタ (3つまで)
st.subheader("🔍 確認する加工品を最大3つまで入力")
col1, col2, col3 = st.columns(3)
with col1:
    item_name1 = st.text_input("加工品 1", "")
with col2:
    item_name2 = st.text_input("加工品 2", "")
with col3:
    item_name3 = st.text_input("加工品 3", "")

# 🔄 操作の種類 ("預ける" "取り出す" "預けた&取り出した")
operation_type = st.selectbox("🔄 操作の種類を選択", ["預ける", "取り出す", "預けた&取り出した"])

# 👋 操作者フィルタ
user_list = ["全員"] + sorted(df["操作者"].unique().tolist())
selected_user = st.selectbox("📋 操作者を選択", user_list)

# 📊 フィルタリング処理
filtered_df = df[(df["日時"].dt.date >= start_date) & (df["日時"].dt.date <= end_date)]

# 🔍 操作種別のフィルタ
if operation_type != "預けた&取り出した":
    filtered_df = filtered_df[filtered_df["操作"] == operation_type]

# 🔍 効果名でフィルタリング
item_filters = [item_name1, item_name2, item_name3]
filtered_df = filtered_df[filtered_df["加工品"].isin([i for i in item_filters if i])]

# 🔍 操作者をフィルタ
if selected_user != "全員":
    filtered_df = filtered_df[filtered_df["操作者"] == selected_user]

# 🔄 取り出すをマイナスとして処理
filtered_df["数量（調整後）"] = filtered_df.apply(
    lambda row: -row["数量"] if row["操作"] == "取り出す" else row["数量"], axis=1
)

# 📚 総集結果
total_quantity = filtered_df["数量（調整後）"].sum()
total_points = filtered_df["同盟ポイント"].sum()

st.subheader(f"📊 {start_date} ～ {end_date} に '{operation_type}' された加工品の合計数量: **{total_quantity}** 個")
st.dataframe(filtered_df.set_index("No"))

st.subheader(f"💰 同盟ポイントの合計: **{total_points}** ポイント")
