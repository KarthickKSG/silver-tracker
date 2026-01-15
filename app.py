import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Nebula Quantum Analytics", page_icon="🌌", layout="wide")

# --- CUSTOM GALAXY THEME & UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        color: #ffffff;
    }
    
    /* Glassmorphism Cards */
    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        text-shadow: 0 0 10px #00d4ff;
        font-family: 'Orbitron', sans-serif;
    }
    
    .css-1r6slb0, .stCard {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 20, 0.95);
        border-right: 1px solid #394481;
    }

    /* Professional Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #7b2ff7);
        color: white; border-radius: 10px; border: none;
        padding: 10px 20px; font-weight: bold; width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #00d4ff;
        transform: scale(1.02);
    }

    /* Logo Styling */
    .logo-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        background: -webkit-linear-gradient(#00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Qk8U4Gx4Zxxb-sTYeCSnMbCz31a2WJiLUMYIsjAcTDY/export?format=csv"

def clean_dataframe(df):
    df.columns = [str(c).strip() for c in df.columns]
    # Find Price Column
    p_col = [c for c in df.columns if 'Price' in c or 'price' in c][0]
    if df[p_col].dtype == 'object':
        df[p_col] = df[p_col].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
    df[p_col] = pd.to_numeric(df[p_col], errors='coerce')
    # Find Date Column
    d_col = [c for c in df.columns if 'Date' in c or 'date' in c][0]
    df[d_col] = pd.to_datetime(df[d_col], errors='coerce')
    return df.dropna(subset=[d_col, p_col]).sort_values(d_col), d_col, p_col

@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url)
        return clean_dataframe(df)
    except:
        return None, None, None

# --- SESSION STATE INITIALIZATION ---
if 'main_df' not in st.session_state:
    df, d_col, p_col = load_data(DEFAULT_SHEET_URL)
    st.session_state.main_df = df
    st.session_state.d_col = d_col
    st.session_state.p_col = p_col

# --- SIDEBAR & LOGO ---
with st.sidebar:
    st.markdown('<p class="logo-text">✨ NEBULA CORE</p>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/1804/1804191.png", width=100)
    st.markdown("---")
    menu = st.radio("MAIN NAVIGATION", 
                   ["🚀 Intelligence Dashboard", "⚖️ Comparison Lab", "🧮 Quantum Calculator", "📁 Archive Manager"],
                   index=0)
    
    st.markdown("---")
    st.subheader("📡 Data Ingestion")
    uploaded_file = st.file_uploader("Upload Secondary CSV", type="csv")
    if uploaded_file:
        df2, d2, p2 = clean_dataframe(pd.read_csv(uploaded_file))
        st.session_state.secondary_df = df2
    
    st.write("System Status: **Optimal** 🟢")

# --- 1. INTELLIGENCE DASHBOARD ---
if menu == "🚀 Intelligence Dashboard":
    st.title("🌌 Cosmic Market Intelligence")
    df = st.session_state.main_df
    d, p = st.session_state.d_col, st.session_state.p_col
    
    # KPI SECTION
    k1, k2, k3, k4 = st.columns(4)
    curr_price = df[p].iloc[-1]
    prev_price = df[p].iloc[-2]
    delta = ((curr_price - prev_price)/prev_price)*100
    
    k1.metric("Current Price", f"₹{curr_price:,.2f}", f"{delta:.2f}%")
    k2.metric("Galaxy Peak", f"₹{df[p].max():,.2f}")
    k3.metric("Market Floor", f"₹{df[p].min():,.2f}")
    k4.metric("Active Cycles", len(df))

    # ADVANCED CHARTS
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        # Interactive Neon Area Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[d], y=df[p], fill='tozeroy', name='Spot Price',
                                 line=dict(color='#00d4ff', width=3),
                                 fillcolor='rgba(0, 212, 255, 0.1)'))
        fig.update_layout(template="plotly_dark", title="Silver Price Quantum Trajectory",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(255,255,255,0.05)'))
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        # Trend Distribution
        if 'Trend' in df.columns:
            fig_pie = px.pie(df, names='Trend', hole=0.7, title="Market Sentiment Mix",
                            color_discrete_sequence=px.colors.sequential.Electric)
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

# --- 2. COMPARISON LAB ---
elif menu == "⚖️ Comparison Lab":
    st.title("⚖️ Dimensional Comparison Engine")
    
    if 'secondary_df' in st.session_state:
        df1 = st.session_state.main_df
        df2 = st.session_state.secondary_df
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(x=df1[st.session_state.d_col], y=df1[st.session_state.p_col], name="Primary Cloud Data"))
        fig_comp.add_trace(go.Scatter(x=df2[st.session_state.d_col], y=df2[st.session_state.p_col], name="Uploaded Data", line=dict(color='#7b2ff7')))
        
        fig_comp.update_layout(template="plotly_dark", title="Cross-Dataset Overlay", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("ℹ️ Please upload a second CSV in the sidebar to enable dual comparison.")

# --- 3. QUANTUM CALCULATOR (Properly Placed) ---
elif menu == "🧮 Quantum Calculator":
    st.title("🧮 Investment Quantum Calculator")
    df = st.session_state.main_df
    p = st.session_state.p_col
    
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        invest_amt = col1.number_input("Investment Amount (₹)", min_value=100.0, value=10000.0)
        buy_price = col2.selectbox("Select Entry Price (Based on History)", df[p].unique())
        target_price = col3.number_input("Target Exit Price (₹)", value=float(df[p].max() * 1.2))
        
        # Calculations
        qty = invest_amt / buy_price
        current_val = qty * target_price
        profit = current_val - invest_amt
        roi = (profit / invest_amt) * 100
        
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.metric("Projected Value", f"₹{current_val:,.2f}")
        res2.metric("Net Profit", f"₹{profit:,.2f}", f"{roi:.2f}%")
        res3.metric("Silver Qty", f"{qty:.3f} Grams")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. ARCHIVE MANAGER ---
elif menu == "📁 Archive Manager":
    st.title("📁 File Management System")
    
    tab1, tab2 = st.tabs(["➕ Add New Record", "📜 Data Ledger"])
    
    with tab1:
        with st.form("data_entry"):
            c1, c2, c3 = st.columns(3)
            nd = c1.date_input("Date")
            np = c2.number_input("Price")
            nt = c3.selectbox("Trend", ["📈 Rising", "📉 Dip", "🔄 Steady", "🚀 Surge"])
            if st.form_submit_button("🚀 Sync to Nebula Cloud"):
                new_row = pd.DataFrame([{st.session_state.d_col: pd.to_datetime(nd), st.session_state.p_col: np, "Trend": nt}])
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_row], ignore_index=True)
                st.success("Synchronized!")

    with tab2:
        st.dataframe(st.session_state.main_df.sort_values(st.session_state.d_col, ascending=False), use_container_width=True)
        csv_data = st.session_state.main_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master Ledger", data=csv_data, file_name="Nebula_Data_Export.csv", mime="text/csv")
