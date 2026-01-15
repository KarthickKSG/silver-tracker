import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Nebula Data Analytics", page_icon="🌌", layout="wide")

# --- GALAXY THEME CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        text-shadow: 0 0 10px #00d4ff;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white; border-radius: 20px; border: none;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
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
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Qk8U4Gx4Zxxb-sTYeCSnMbCz31a2WJiLUMYIsjAcTDY/export?format=csv"

@st.cache_data(ttl=600)
def load_initial_data():
    try:
        # Load data
        df = pd.read_csv(SHEET_URL)
        
        # CLEANING: Remove leading/trailing spaces from column names
        df.columns = df.columns.str.strip()
        
        # DATE CONVERSION: Handle different date formats
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        
        # NUMERIC CONVERSION: Ensure Sales and Profit are numbers
        for col in ['Sales', 'Profit', 'Discount', 'Quantity']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return pd.DataFrame()

# Initialize Session State
if 'main_df' not in st.session_state:
    st.session_state.main_df = load_initial_data()

df = st.session_state.main_df

# --- SIDEBAR ---
with st.sidebar:
    st.title("📈 Nebula Systems")
    page = st.radio("Navigation", ["Live Dashboard", "Comparison Tool", "Data Management"])
    st.markdown("---")
    if st.button("🔄 Refresh Cloud Data"):
        st.session_state.main_df = load_initial_data()
        st.rerun()

# --- VALIDATION CHECK ---
required_columns = ['Sales', 'Profit', 'Category']
missing_cols = [c for c in required_columns if c not in df.columns]

if missing_cols:
    st.error(f"❌ Critical Error: The columns {missing_cols} were not found in your sheet.")
    st.write("Columns found in your sheet:", list(df.columns))
    st.stop()

# --- PAGE 1: DASHBOARD ---
if page == "Live Dashboard":
    st.title("🚀 Cosmic Analytics Dashboard")
    
    # TOP ROW KPIs
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Sales", f"${df['Sales'].sum():,.0f}")
    m2.metric("Net Profit", f"${df['Profit'].sum():,.0f}")
    m3.metric("Total Orders", f"{len(df):,}")
    m4.metric("Avg Discount", f"{df['Discount'].mean()*100:.1f}%")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sales Trend
        if 'Order Date' in df.columns:
            df_trend = df.groupby(df['Order Date'].dt.date)['Sales'].sum().reset_index()
            fig = px.area(df_trend, x='Order Date', y='Sales', title="Revenue Stream Over Time",
                         color_discrete_sequence=['#00d4ff'])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category breakdown
        fig2 = px.pie(df, values='Sales', names='Category', hole=.5, title="Category Mix")
        fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

# --- PAGE 2: COMPARISON TOOL ---
elif page == "Comparison Tool":
    st.title("⚖️ Performance Comparison")
    
    # Compare by Region or Category
    compare_on = st.selectbox("Compare performance based on:", ["Region", "Segment", "Ship Mode"])
    
    if compare_on in df.columns:
        options = df[compare_on].unique()
        col1, col2 = st.columns(2)
        with col1:
            a = st.selectbox(f"Select {compare_on} A", options, index=0)
        with col2:
            b = st.selectbox(f"Select {compare_on} B", options, index=1 if len(options)>1 else 0)
            
        comp_df = df[df[compare_on].isin([a, b])]
        fig = px.bar(comp_df, x='Category', y='Sales', color=compare_on, barmode='group',
                    title=f"Comparison: {a} vs {b}")
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 3: DATA MANAGEMENT ---
elif page == "Data Management":
    st.title("📁 Ledger & File Management")
    
    # 1. Add New Data Option
    with st.expander("➕ Inject New Data Entry"):
        with st.form("entry_form"):
            c1, c2, c3 = st.columns(3)
            new_id = c1.text_input("Order ID", "CA-2024-NEW")
            new_sales = c2.number_input("Sales Value", min_value=0.0)
            new_profit = c3.number_input("Profit Value")
            
            c4, c5 = st.columns(2)
            new_cat = c4.selectbox("Category", df['Category'].unique() if 'Category' in df.columns else ["Default"])
            new_reg = c5.selectbox("Region", df['Region'].unique() if 'Region' in df.columns else ["Default"])
            
            if st.form_submit_button("🚀 Upload to Dashboard"):
                new_data = pd.DataFrame([{
                    "Order ID": new_id, "Sales": new_sales, "Profit": new_profit,
                    "Category": new_cat, "Region": new_reg, "Order Date": pd.Timestamp.now(),
                    "Discount": 0, "Quantity": 1
                }])
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_data], ignore_index=True)
                st.success("New record integrated into the system!")
                st.rerun()

    # 2. File Download Management
    st.write("### Current System Data")
    st.dataframe(st.session_state.main_df, use_container_width=True)
    
    csv = st.session_state.main_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Database as CSV", data=csv, file_name="galaxy_export.csv", mime="text/csv")
