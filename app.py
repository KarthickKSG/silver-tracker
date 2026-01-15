import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Nebula Data Analytics", page_icon="🌌", layout="wide")

# --- GALAXY CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        text-shadow: 0 0 10px #00d4ff;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white; border-radius: 20px; border: none;
    }
    /* Glassmorphism containers */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
SHEET_ID = "1Qk8U4Gx4Zxxb-sTYeCSnMbCz31a2WJiLUMYIsjAcTDY"
# Securely format the Google Sheet Export Link
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600) # Refresh data every 10 mins
def load_initial_data():
    try:
        df = pd.read_csv(URL)
        # Clean column names and convert dates
        df.columns = df.columns.str.strip()
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'])
        return df
    except Exception as e:
        st.error(f"Error connecting to Galaxy Data Source: {e}")
        return pd.DataFrame()

if 'main_df' not in st.session_state:
    st.session_state.main_df = load_initial_data()

df = st.session_state.main_df

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌌 Nebula Systems")
    page = st.radio("Navigation", ["Dashboard", "Comparison Tool", "Data Management"])
    st.markdown("---")
    st.write("**System Status:** Operational ✅")

# --- PAGE 1: DASHBOARD ---
if page == "Dashboard":
    st.title("🚀 Cosmic Analytics Dashboard")
    
    if not df.empty:
        # KPIs
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sales", f"${df['Sales'].sum():,.0f}")
        m2.metric("Total Profit", f"${df['Profit'].sum():,.0f}")
        m3.metric("Orders", f"{len(df):,}")
        m4.metric("Avg Discount", f"{df['Discount'].mean()*100:.1f}%")

        c1, c2 = st.columns([2, 1])
        with c1:
            # Time Analysis
            df_trend = df.groupby(df['Order Date'].dt.date)['Sales'].sum().reset_index()
            fig = px.line(df_trend, x='Order Date', y='Sales', title="Sales Over Time")
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            # Category Analysis
            fig2 = px.pie(df, values='Sales', names='Category', hole=.4, title="Category Mix")
            fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# --- PAGE 2: COMPARISON ---
elif page == "Comparison Tool":
    st.title("⚖️ Dimensional Comparison")
    col1, col2 = st.columns(2)
    with col1:
        dim = st.selectbox("Select Region A", df['Region'].unique(), index=0)
    with col2:
        dim2 = st.selectbox("Select Region B", df['Region'].unique(), index=1)
    
    comp_df = df[df['Region'].isin([dim, dim2])]
    fig = px.bar(comp_df, x='Category', y='Sales', color='Region', barmode='group')
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 3: DATA MANAGEMENT ---
elif page == "Data Management":
    st.title("📁 Ledger Management")
    
    with st.expander("➕ Add New Order"):
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            o_id = c1.text_input("Order ID")
            o_sales = c2.number_input("Sales")
            o_cat = st.selectbox("Category", df['Category'].unique())
            if st.form_submit_button("Sync New Data"):
                new_row = pd.DataFrame([{"Order ID": o_id, "Sales": o_sales, "Category": o_cat, "Order Date": datetime.now(), "Profit": 0, "Region": "Central"}])
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_row], ignore_index=True)
                st.rerun()

    st.dataframe(st.session_state.main_df, use_container_width=True)
