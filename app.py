# my-cpm-calculator
import streamlit as st
import pandas as pd
import requests
import re

# 设置网页标题
st.set_page_config(page_title="全球社媒 CPM 智能计算器", layout="wide")
st.title("📊 全球社媒 CPM 智能计算器 (Vibes Edition)")
st.caption("支持单次/批量计算，IG/TT/YTB 链接自动识别均播")

# ==========================================
# 1. 模拟 API 调用模块 (实际使用填入你的第三方API Key)
# ==========================================
# 提示：实际推荐对接 NoxInfluencer 或 Modash 等 API
API_KEY = "YOUR_MOCK_API_KEY" 

def fetch_average_views_from_api(url):
    """通过第三方网红数据API，根据链接识别均播"""
    if not url:
        return 0
    
    # 简单的平台正则识别
    platform = None
    if "tiktok.com" in url: platform = "TikTok"
    elif "instagram.com" in url or "ig.me" in url: platform = "Instagram"
    elif "youtube.com" in url or "youtu.be" in url: platform = "YouTube"
    
    if not platform:
        return 0
        
    try:
        # 这里模拟请求第三方数据聚合 API
        # 实际代码类似：response = requests.get(f"https://api.modash.io/v1/profile?url={url}", headers={"Authorization": API_KEY})
        # 这里用模拟数据代替真实返回
        mock_database = {
            "TikTok": 45000,
            "Instagram": 12000,
            "YouTube": 85000
        }
        return mock_database.get(platform, 0)
    except Exception:
        return 0

# ==========================================
# 2. 核心计算函数
# ==========================================
def calc_cpm(views, price):
    return round((price / views) * 1000, 2) if views > 0 else 0

def calc_budget(views, cpm):
    return round((views * cpm) / 1000, 2)

# ==========================================
# 3. 前端 UI 布局
# ==========================================
tab1, tab2 = st.tabs(["🎯 单个/链接快捷计算", "📂 批量导入计算 (CSV/Excel)"])

# ----- TAB 1: 单个计算 -----
with tab1:
    st.header("单个直算 / 链接识别")
    col1, col2 = st.columns(2)
    
    with col1:
        calc_type = st.radio("选择计算模式：", ["已知均播/价格 $\rightarrow$ 算 CPM", "已知均播/目标CPM $\rightarrow$ 算预算"])
        link_input = st.text_input("🔗 粘贴红人主页/视频链接 (支持 IG, TikTok, YouTube)", placeholder="https://www.tiktok.com/@...")
        
        # 链接识别按钮
        input_views = 0
        if link_input:
            with st.spinner("正在通过 API 提取该账号近期均播量..."):
                api_views = fetch_average_views_from_api(link_input)
                if api_views > 0:
                    st.success(f"✅ 成功识别平台！该账号预估近期均播量: {api_views:,}")
                    input_views = api_views
                else:
                    st.warning("⚠️ 无法从链接提取数据，请手动在下方输入均播。")
        
        # 手动修正/输入均播
        views = st.number_input("👁️ 均播量 (Views)", min_value=0, value=int(input_views) if input_views else 10000, step=1000)

    with col2:
        if "算 CPM" in calc_type:
            price = st.number_input("💰 达人报价/价格 ($)", min_value=0.0, value=500.0, step=50.0)
            st.markdown("---")
            if views > 0:
                res_cpm = calc_cpm(views, price)
                st.metric(label="📊 计算出的 CPM", value=f"${res_cpm}")
        else:
            target_cpm = st.number_input("🎯 目标 CPM ($)", min_value=0.0, value=20.0, step=1.0)
            st.markdown("---")
            res_budget = calc_budget(views, target_cpm)
            st.metric(label="💰 建议投放预算", value=f"${res_budget}")

# ----- TAB 2: 批量导入 -----
with tab2:
    st.header("批量导入与计算")
    st.write("请上传包含 `链接` 或 `均播` 的表格，系统会自动调用 API 补全并计算。")
    
    # 提供一个模板下载暗示
    st.markdown("""
    💡 **支持的表头字段**：`达人名称`, `链接` (或 `均播`), `价格` (算CPM填), `目标CPM` (算预算填)
    """)
    
    uploaded_file = st.file_uploader("选择 Excel 或 CSV 文件", type=["csv", "xlsx"])
    
    if uploaded_file:
        # 读取数据
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.subheader("📦 原始数据预览")
        st.dataframe(df.head(5))
        
        if st.button("🚀 开始批量解析并计算"):
            with st.spinner("正在批量调用 API 识别链接并计算中..."):
                
                # 确保必要的列存在
                if '均播' not in df.columns:
                    df['均播'] = 0
                
                # 1. 遍历解析链接
                if '链接' in df.columns:
                    for idx, row in df.iterrows():
                        if pd.notna(row['链接']) and (row['均播'] == 0 or pd.isna(row['均播'])):
                            df.at[idx, '均播'] = fetch_average_views_from_api(str(row['链接']))
                
                # 2. 执行双向计算
                calculated_cpm_list = []
                calculated_budget_list = []
                
                for idx, row in df.iterrows():
                    v = float(row['均播']) if pd.notna(row['均播']) else 0
                    
                    # 算CPM
                    if '价格' in df.columns and pd.notna(row['价格']):
                        calculated_cpm_list.append(calc_cpm(v, float(row['价格'])))
                    else:
                        calculated_cpm_list.append(None)
                        
                    # 算预算
                    if '目标CPM' in df.columns and pd.notna(row['目标CPM']):
                        calculated_budget_list.append(calc_budget(v, float(row['目标CPM'])))
                    else:
                        calculated_budget_list.append(None)
                
                if any(x is not None for x in calculated_cpm_list):
                    df['计算出_CPM'] = calculated_cpm_list
                if any(x is not None for x in calculated_budget_list):
                    df['计算出_预算'] = calculated_budget_list
                    
                st.subheader("✨ 计算结果")
                st.dataframe(df)
                
                # 下载按钮
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 下载结果表格", data=csv, file_name="cpm_results.csv", mime="text/csv")
