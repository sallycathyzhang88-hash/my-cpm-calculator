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
# 1. 核心智能文本清洗与多平台拆分模块
# ==========================================
def parse_platform_value(text_val, preference):
    """
    智能拆分清洗函数：
    支持 'IG 1100, TT600' 或 'IG: $200 / TT: $500'
    根据 preference ('TT', 'IG', 'YT') 提取对应平台的纯数字，并转换 K/M 单位
    """
    if pd.isna(text_val):
        return 0.0
    
    val_str = str(text_val).strip().upper()
    if not val_str:
        return 0.0
        
    # 匹配标识
    pattern_map = {
        'TT': [r'TT[:\s]*([0-9\.,]+[KM]?)', r'TIKTOK[:\s]*([0-9\.,]+[KM]?)'],
        'IG': [r'IG[:\s]*([0-9\.,]+[KM]?)', r'INS[:\s]*([0-9\.,]+[KM]?)', r'INSTAGRAM[:\s]*([0-9\.,]+[KM]?)'],
        'YT': [r'YT[:\s]*([0-9\.,]+[KM]?)', r'YTB[:\s]*([0-9\.,]+[KM]?)', r'YOUTUBE[:\s]*([0-9\.,]+[KM]?)']
    }
    
    target_text = None
    for pattern in pattern_map.get(preference, []):
        match = re.search(pattern, val_str)
        if match:
            target_text = match.group(1)
            break
            
    if not target_text:
        target_text = val_str

    try:
        multiplier = 1.0
        if 'K' in target_text:
            multiplier = 1000.0
            target_text = target_text.replace('K', '')
        elif 'M' in target_text:
            multiplier = 1000000.0
            target_text = target_text.replace('M', '')
            
        cleaned_str = re.sub(r'[^\d\.]', '', target_text)
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
    st.markdown("<p style='color:#64748B; font-size:15px; margin-top:-10px;'>跨平台传播成本双向测算系统 · 支持双向双字段全清洗</p>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. 核心功能标签页 (Tabs)
# ==========================================
tab1, tab2 = st.tabs(["🎯 单测 · 智能链路透视", "📂 批处理 · 混合数据清洗表"])

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
            single_pref = st.selectbox("🎯 单测平台数据提取偏好：", ["TT", "IG", "YT"], index=0)
            
            raw_views_input = st.text_input("👁️ 预估平均播放量", value="IG 1100, TT600")
            views = parse_platform_value(raw_views_input, single_pref)
            
            if "求 CPM" in calc_type:
                raw_price_input = st.text_input("💰 达人合作报价", value="IG: $200, TT: $500")
                price = parse_platform_value(raw_price_input, single_pref)
            else:
                raw_cpm_input = st.text_input("🎯 目标期望 CPM", value="$20")
                target_cpm = parse_platform_value(raw_cpm_input, single_pref)
                    
        with col_right:
            st.markdown("### 📊 测算交付结果")
            if "求 CPM" in calc_type:
                st.write(f"⚙️ *系统识别 ➔ 清洗后【{single_pref}】均播: **{views:,.0f}** | 清洗后【{single_pref}】价格: **${price:,.2f}***")
                res_cpm = calc_cpm(views, price)
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-title">💵 Calculated CPM (千次展示成本)</div>
                        <div class="metric-card-value">${res_cpm:,}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.write(f"⚙️ *系统识别 ➔ 清洗后【{single_pref}】均播: **{views:,.0f}** | 清洗后目标 CPM: **${target_cpm:,.2f}***")
                res_budget = calc_budget(views, target_cpm)
                st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #0EA5E9, #2563EB);">
                        <div class="metric-card-title">💰 Recommended Budget (建议匹配预算)</div>
                        <div class="metric-card-value">${res_budget:,}</div>
                    </div>
                """, unsafe_allow_html=True)

# ----- TAB 2: 批量混合清洗 -----
with tab2:
    with st.container(border=True):
        st.markdown("### 📂 混合/多平台脏数据智能清洗")
        
        uploaded_file = st.file_uploader("将包含混合数据的 Excel / CSV 表格拖拽至此", type=["csv", "xlsx"])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            
            st.markdown("#### 📥 导入原始队列预览")
            st.dataframe(df, use_container_width=True, height=150)
            
            cols = df.columns.tolist()
            st.markdown("##### 🔍 智能配置与核心平台提取偏好")
            col_sel1, col_sel2, col_sel3 = st.columns(3)
            with col_sel1:
                views_col = st.selectbox("请指定【均播量】所在的列：", cols, index=cols.index('均播') if '均播' in cols else 0)
            with col_sel2:
                price_col = st.selectbox("请指定【价格/报价】所在的列：", cols, index=cols.index('价格') if '价格' in cols else 0)
            with col_sel3:
                batch_pref = st.radio("🎯 本次批量计算【核心锁定平台】", ["TT", "IG", "YT"], index=0, horizontal=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 启动混合多平台全量测算 Pipeline", type="primary"):
                with st.spinner(f"正在智能剥离并精确提取【{batch_pref}】数据中..."):
                    
                    output_df = df.copy()
                    
                    # 运行多平台条件清洗
                    clean_views = output_df[views_col].apply(lambda x: parse_platform_value(x, batch_pref))
                    clean_prices = output_df[price_col].apply(lambda x: parse_platform_value(x, batch_pref))
                    
                    is_calculating_budget = 'CPM' in price_col.upper() or '目标' in price_col
                    
                    cpm_out = []
                    budget_out = []
                    
                    for v, p in zip(clean_views, clean_prices):
                        if is_calculating_budget:
                            cpm_out.append(p)
                            budget_out.append(calc_budget(v, p))
                        else:
                            cpm_out.append(calc_cpm(v, p))
                            budget_out.append(p)
                    
                    # === 核心改动：两列同时输出清洗后的干净纯数字 ===
                    output_df[f'清洗后_{batch_pref}_均播'] = clean_views
                    output_df[f'清洗后_{batch_pref}_价格'] = clean_prices
                    
                    if is_calculating_budget:
                        output_df[f'输出结果_建议预算($)'] = budget_out
                    else:
                        output_df[f'输出结果_智能CPM($)'] = cpm_out
                    
                    st.balloons() 
                    st.markdown(f"#### ✨ 提取成功！均播和价格已全部转换为干净数字：")
                    st.dataframe(output_df, use_container_width=True)
                    
                    csv = output_df.to_csv(index=False).encode('utf-8')
                    st.download_button(f"📥 导出【{batch_pref}】专项测算报表 (CSV)", data=csv, file_name=f"cpm_{batch_pref}_output.csv", mime="text/csv")
