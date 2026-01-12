import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# =========================
# 页面设置
# =========================
st.set_page_config(
    page_title="Stock Screening App",
    layout="wide"
)

st.title("📈 Interactive Stock Screening System")
st.write("Upload financial data and customize screening rules.")

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# =========================
# Step 1: 文件上传
# =========================
uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.warning("Please upload an Excel file to continue.")
    st.stop()

df = pd.read_excel(uploaded_file)

st.success("Data loaded successfully!")

# =========================
# Step 2: 指定列名（与你原代码一致）
# =========================
name_col = "最新股票名称_Lstknm"
eps_col  = "每股收益(摊薄)(元/股)_EPS"
roe_col  = "净资产收益率(摊薄)(%)_ROE"
pe_col   = "市盈率_PE"
pb_col   = "市净率_PB"

required_cols = [name_col, eps_col, roe_col, pe_col, pb_col]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

df = df[required_cols].dropna()
df = df[(df[pe_col] > 0) & (df[pb_col] > 0)]

# =========================
# Step 3: 侧边栏 – 交互筛选条件
# =========================
st.sidebar.header("🔧 Screening Criteria")

min_eps = st.sidebar.number_input(
    "Minimum EPS",
    value=0.0,
    step=0.1
)

min_roe = st.sidebar.slider(
    "Minimum ROE (%)",
    min_value=0,
    max_value=50,
    value=10
)

max_pe = st.sidebar.slider(
    "Maximum PE",
    min_value=0,
    max_value=100,
    value=30
)

max_pb = st.sidebar.slider(
    "Maximum PB",
    min_value=0.0,
    max_value=10.0,
    value=2.0
)

# =========================
# Step 4: 执行筛选
# =========================
filtered = df[
    (df[eps_col] > min_eps) &
    (df[roe_col] > min_roe) &
    (df[pe_col] < max_pe) &
    (df[pb_col] < max_pb)
].sort_values(by=roe_col, ascending=False)

# =========================
# Step 5: 显示结果表
# =========================
st.subheader("📋 Screening Results")
st.write(f"Selected stocks: **{len(filtered)}**")

st.dataframe(filtered, use_container_width=True)

# =========================
# Step 6: 下载结果
# =========================
output_file = "stock_screening_results.xlsx"
filtered.to_excel(output_file, index=False)

with open(output_file, "rb") as f:
    st.download_button(
        label="⬇️ Download Excel",
        data=f,
        file_name=output_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =========================
# Step 7: 可视化
# =========================
st.subheader("📊 Visualization")

top10 = filtered.head(10)

if len(top10) > 0:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top10[name_col], top10[roe_col])
    ax.set_xlabel("ROE (%)")
    ax.set_title("Top 10 Stocks by ROE")
    st.pyplot(fig)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(top10[name_col], top10[pe_col], label="PE")
    ax2.bar(top10[name_col], top10[pb_col], bottom=top10[pe_col], label="PB")
    ax2.set_title("PE + PB Comparison")
    ax2.legend()
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig2)
else:
    st.info("No stocks meet the selected criteria.")
