import plotly.express as px
import pandas as pd
import streamlit as st

# 页面设置
st.set_page_config(page_title="Stock Screening App", layout="wide")

st.title("📈 Interactive Stock Screening System")
st.write("Upload financial data and customize screening rules.")

# 上传 Excel 文件
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is None:
    st.warning("Please upload an Excel file to continue.")
    st.stop()

df = pd.read_excel(uploaded_file)

st.success("Data loaded successfully!")

# 筛选必要的列
name_col = "最新股票名称_Lstknm"
eps_col = "每股收益(摊薄)(元/股)_EPS"
roe_col = "净资产收益率(摊薄)(%)_ROE"
pe_col = "市盈率_PE"
pb_col = "市净率_PB"

required_cols = [name_col, eps_col, roe_col, pe_col, pb_col]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

df = df[required_cols].dropna()
df = df[(df[pe_col] > 0) & (df[pb_col] > 0)]

# 侧边栏 – 交互筛选条件
min_eps = st.sidebar.number_input("Minimum EPS", value=0.0, step=0.1)
min_roe = st.sidebar.slider("Minimum ROE (%)", min_value=0, max_value=50, value=10)
max_pe = st.sidebar.slider("Maximum PE", min_value=0, max_value=100, value=30)
max_pb = st.sidebar.slider("Maximum PB", min_value=0.0, max_value=10.0, value=2.0)

# 侧边栏 – 选择显示的股票数量（从 1 到 10）
top_n = st.sidebar.slider("Number of top stocks to display", min_value=1, max_value=10, value=5)

# 执行筛选
filtered = df[
    (df[eps_col] > min_eps) &
    (df[roe_col] > min_roe) &
    (df[pe_col] < max_pe) &
    (df[pb_col] < max_pb)
].sort_values(by=roe_col, ascending=False)

# 显示筛选结果
st.subheader("📋 Screening Results")
st.write(f"Selected stocks: **{len(filtered)}**")
st.dataframe(filtered)

# 使用 Plotly 生成图表
st.subheader("📊 Visualization")

# 根据选择的数量获取前 N 个股票
top_stocks = filtered.head(top_n)

if len(top_stocks) > 0:
    # Top N ROE 股票
    fig = px.bar(top_stocks, 
                 y=name_col, 
                 x=roe_col, 
                 orientation="h", 
                 title="Top Stocks by ROE", 
                 labels={roe_col: "ROE (%)", name_col: "Stock Name"})
    st.plotly_chart(fig)

    # PE + PB 比较
    fig2 = px.bar(top_stocks, 
                  x=name_col, 
                  y=[pe_col, pb_col], 
                  title="PE + PB Comparison", 
                  labels={name_col: "Stock Name", pe_col: "PE", pb_col: "PB"})
    st.plotly_chart(fig2)
else:
    st.info("No stocks meet the selected criteria.")
