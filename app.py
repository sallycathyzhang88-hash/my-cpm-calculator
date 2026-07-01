import streamlit as st
import pandas as pd
import requests
import re

# ==========================================
# 0. 全局样式定制（大厂科技感 UI）
# ==========================================
st.set_page_config(
    page_title="Global Media CPM Planner", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { font-weight: 800 !important; color: #1E293B; letter-spacing: -0.5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: #F8FAFC;
        border-radius: 8px;
        color: #64748B;
        font-weight: 600;
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: white !important;
        border-color: #4F46E5 !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        padding: 24px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
        margin-top: 15px;
    }
    .metric-card-title { font-size: 14px; opacity: 0.85; font-weight: 500; }
    .metric-card-value { font-size: 36px; font-weight: 700; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 核心智能文本清洗模块（解决脏数据 Bug）
# ==========================================
def clean_and_convert_num(text_val):
    """
    终极清洗函数：把 ' $15,000 ', ' 23.5K ', ' 1.2M ', ' 500 USD ' 统一清洗成标准数字 float
    """
    if pd.isna(text_val):
        return 0.0
    
    # 转为字符串并去掉两端空格，转大写
    val_str = str(text_val).strip().upper()
    
    if not val_str:
        return 0.0
        
    try:
        # 1. 检查有没有带 K、M 等社媒常用缩写单位
        multiplier = 1.0
        if 'K' in val_str:
            multiplier = 1000.0
            val_str = val_str.replace('K', '')
        elif 'M' in val_str:
            multiplier = 1000000.0
            val_str = val_str.replace('M', '')
            
        # 2. 剥离掉所有非数字、非小数点的杂质（比如 $, ￥, USD, 逗号）
        cleaned_str = re.sub(r'[^\d\.]', '', val_str)
        
        if not cleaned_str:
            return 0.0
            
        return float(cleaned_str) * multiplier
    except Exception:
        return 0.0

def calc_cpm(views, price): 
    return round((price / views) * 1000, 2) if views > 0 else 0

def calc_budget(views, cpm): 
    return round((views * cpm) / 1000, 2)

# ==========================================
# 2. 顶栏设计 (Header)
# ==========================================
col_logo, col_title = st.columns([1, 15])
with col_title:
    st.markdown("# 📈 全球社媒 CPM 智能规划看板")
    st.markdown("<p style='color:#64748B; font-size:15px; margin-top:-10px;'>跨平台传播成本双向测算系统 · 内置脏数据智能清洗 Pipeline</p>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. 核心功能标签页 (Tabs)
# ==========================================
tab1, tab2 = st.tabs(["🎯 单测 · 智能链路透视", "📂 批处理 · 智能清洗大表"])

# ----- TAB 1: 快捷单测 -----
with tab1:
    with st.container(border=True):
        col_left, col_right = st.columns([1.1, 0.9], gap="large")
        
        with col_left:
            st.markdown("### 📋 策略与输入")
            calc_type = st.segmented_control(
                "测算模式选择",
                options=["求 CPM (已知报价)", "求预算 (已知目标CPM)"],
                default="求 CPM (已知报价)"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            # 单次测算也支持输入带文字的数据
            raw_views_input = st.text_input("👁️ 预估平均播放量 (支持输入 15k, 1.2M, 25,000 等)", value="25,000")
            views = clean_and_convert_num(raw_views_input)
            
            if "求 CPM" in calc_type:
                raw_price_input = st.text_input("💰 达人合作报价 (支持输入 $500, 500 USD 等)", value="$500")
                price = clean_and_convert_num(raw_price_input)
            else:
                raw_cpm_input = st.text_input("🎯 目标期望 CPM (支持输入 $20 等)", value="$20")
                target_cpm = clean_and_convert_num(raw_cpm_input)
                    
        with col_right:
            st.markdown("### 📊 测算交付结果")
            st.write(f"⚙️ *系统识别到真实计算数据 ➔ 均播: **{views:,.0f}** | 价格/CPM: **{price if '求 CPM' in calc_type else target_cpm:,.2f}***")
            
            if "求 CPM" in calc_type:
                res_cpm = calc_cpm(views, price)
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-title">💵 Calculated CPM (千次展示成本)</div>
                        <div class="metric-card-value">${res_cpm:,}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                res_budget = calc_budget(views, target_cpm)
                st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #0EA5E9, #2563EB);">
                        <div class="metric-card-title">💰 Recommended Budget (建议匹配预算)</div>
                        <div class="metric-card-value">${res_budget:,}</div>
                    </div>
                """, unsafe_allow_html=True)

# ----- TAB 2: 批量清洗与处理 -----
with tab2:
    with st.container(border=True):
        st.markdown("### 📂 脏数据智能清洗矩阵导入")
        st.markdown("<p style='color:#64748B; font-size:14px; margin-top:-10px;'>无论你的表格数据带不带符号、带不带 <b>K/M</b> 单位，系统都会在后台自动清洗纯化并输出标准结果。</p>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("将包含【均播】和【价格】（或目标CPM）的 Excel / CSV 表格拖拽至此", type=["csv", "xlsx"])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            
            st.markdown("#### 📥 导入待清洗队列预览")
            st.dataframe(df, use_container_width=True, height=180)
            
            # 自动检测表头
            cols = df.columns.tolist()
            st.markdown("##### 🔍 字段智能映射确诊")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                views_col = st.selectbox("请指定【均播量】对应的列名：", cols, index=cols.index('均播') if '均播' in cols else 0)
            with col_sel2:
                price_col = st.selectbox("请指定【价格/报价】对应的列名（若算预算，请选目标CPM列）：", cols, index=cols.index('价格') if '价格' in cols else (cols.index('目标CPM') if '目标CPM' in cols else 0))
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 启动数据清洗与全量测算 Pipeline", type="primary"):
                with st.spinner("智能引擎正在脱敏、转换单位并计算中..."):
                    
                    output_df = df.copy()
                    
                    # 运行全自动清洗核心
                    clean_views = output_df[views_col].apply(clean_and_convert_num)
                    clean_prices = output_df[price_col].apply(clean_and_convert_num)
                    
                    # 动态判定用户是想算 CPM 还是算预算
                    is_calculating_budget = 'CPM' in price_col.upper() or '目标' in price_col
                    
                    cpm_out = []
                    budget_out = []
                    
                    for v, p in zip(clean_views, clean_prices):
                        if is_calculating_budget:
                            cpm_out.append(p) # 输入的本来就是CPM
                            budget_out.append(calc_budget(v, p))
                        else:
                            cpm_out.append(calc_cpm(v, p))
                            budget_out.append(p) # 输入的是价格
                    
                    # 将清洗后的真实数值和计算结果追加进最终导出的表里
                    output_df['系统识别_清洗后均播'] = clean_views
                    if is_calculating_budget:
                        output_df['输出结果_建议预算($)'] = budget_out
                    else:
                        output_df['输出结果_智能CPM($)'] = cpm_out
                    
                    st.balloons() 
                    st.markdown("#### ✨ 清洗计算交付表 (包含全新生成的计算结果列)")
                    st.dataframe(output_df, use_container_width=True)
                    
                    csv = output_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 一键导出标准全量报表 (CSV)", data=csv, file_name="cpm_cleaned_output.csv", mime="text/csv")
