import os
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.font_manager import FontProperties
import pandas as pd
import streamlit as st

# =========================
# 页面设置
# =========================
st.set_page_config(
    page_title="Stock Screening App",
    layout="wide"
)

# =========================
# 页面样式优化
# =========================
st.markdown("""
<style>
    .reportview-container {
        background-color: #f4f4f4; /* 页面背景颜色 */
    }
    .sidebar .sidebar-content {
        background-color: #ececec; /* 侧边栏背景颜色 */
    }
    body {
        font-family: "Arial Unicode MS", sans-serif;
        background-color: #fafafa; /* 整体背景颜色 */
    }
    .css-1v3fvcr {
        color: #4a4a4a; /* 修改表格文字颜色 */
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Interactive Stock Screening System")
st.write("Upload financial data and customize screening rules.")

# =========================
# 字体加载：优先使用 repo 中的字体文件（fonts/），否则在系统字体中查找中文字体
# =========================
chinese_fp = None
font_path_repo = os.path.join("fonts", "NotoSansSC-Regular.otf")  # 推荐放置此字体到 repo/fonts/

def try_use_font_from_path(path):
    try:
        fm.fontManager.addfont(path)
        fp = FontProperties(fname=path)
        # 设置 rcParams 以便 matplotlib 默认使用该字体
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [fp.get_name()]
        return fp
    except Exception:
        return None

# 优先使用仓库内字体文件
if os.path.exists(font_path_repo):
    chinese_fp = try_use_font_from_path(font_path_repo)

# 如果没有提供仓库字体，尝试在系统字体中寻找常见中文字体
if chinese_fp is None:
    # 常见中文字体关键字（按优先级）
    preferred_keywords = ["Noto", "Noto Sans", "NotoSans", "SimHei", "Microsoft Yahei", "YaHei", "WenQuanYi", "Source Han", "思源", "黑体", "宋体", "方正"]
    for f in fm.fontManager.ttflist:
        name = f.name or ""
        fname = f.fname or ""
        # 如果字体名或文件名包含关键字，则尝试使用
        if any(k.lower() in name.lower() for k in preferred_keywords) or any(k.lower() in fname.lower() for k in preferred_keywords):
            try:
                chinese_fp = FontProperties(fname=f.fname)
                plt.rcParams["font.family"] = "sans-serif"
                plt.rcParams["font.sans-serif"] = [chinese_fp.get_name()]
                break
            except Exception:
                chinese_fp = None

# 保证负号正常显示
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
# Step 2: 指定列名
# =========================
name_col = "最新股票名称_Lstknm"
eps_col  = "每股收益(摊薄)(元/股)_EPS"
roe_col  = "净资产收益率(摊薄)(%)_ROE"
pe_col   = "市盈率_PE"
pb_col   = "市净率_PB"

required_cols = [name_col, eps_col, roe_col, pe_col, pb_col]

# 校验必要的列是否存在
for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

df = df[required_cols].dropna()  # 删除缺失值
# 过滤掉非正的 PE/PB
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
# Step 7: 可视化（仅当有数据时）
# =========================
st.subheader("📊 Visualization")

top10 = filtered.head(10)

if len(top10) == 0:
    st.info("No stocks meet the selected criteria.")
else:
    # 图表 1: ROE 排序（横向条形图）
    fig, ax = plt.subplots(figsize=(10, 6))
    # 使用 y 轴为股票名，x 为 ROE
    ax.barh(top10[name_col], top10[roe_col], color="#2b8cbe")
    ax.set_xlabel("ROE (%)")
    ax.set_title("Top 10 Stocks by ROE")

    # 为 yticklabels 设置中文字体（如果可用）
    if chinese_fp is not None:
        for label in ax.get_yticklabels():
            label.set_fontproperties(chinese_fp)
        ax.xaxis.label.set_fontproperties(chinese_fp)
        ax.yaxis.label.set_fontproperties(chinese_fp)
        ax.title.set_fontproperties(chinese_fp)
    # 反转 y 轴以使最大值在顶部（常见习惯）
    ax.invert_yaxis()
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

    # 图表 2: PE 和 PB 比较（柱状堆叠）
    names = top10[name_col].tolist()
    x = range(len(names))

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.bar(x, top10[pe_col], label="PE", color="#7fbf7b")
    ax2.bar(x, top10[pb_col], bottom=top10[pe_col], label="PB", color="#d95f02")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=45, ha="right")
    ax2.set_title("PE + PB Comparison")
    ax2.set_ylabel("Value")
    ax2.legend()

    # 字体设置
    if chinese_fp is not None:
        for label in ax2.get_xticklabels():
            label.set_fontproperties(chinese_fp)
        ax2.xaxis.label.set_fontproperties(chinese_fp)
        ax2.yaxis.label.set_fontproperties(chinese_fp)
        ax2.title.set_fontproperties(chinese_fp)

    plt.tight_layout()
    st.pyplot(fig2, use_container_width=True)
