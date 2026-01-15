import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Nebula Silver Analytics", page_icon="🌌", layout="wide")

# --- GALAXY THEME CSS ---
st.markdown("""
    <style>
    /* Global Galaxy Background */
    .stApp {
        background: radial-gradient(circle at top right, #0b0e1e, #16213e, #0f3460);
        color: #e0e0e0;
    }
    
    /* Glassmorphism Containers */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }

    /* Neon Titles */
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 0 0 15px #00d4ff;
        font-family: 'Orbitron', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 25, 0.9);
    }

    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #7b2ff7, #00d4ff);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #00d4ff;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA PROCESSING ENGINE ---
def clean_data(df):
    # Remove Currency symbol and convert to float
    if 'Price (Per Gram)' in df.columns:
        if df['Price (Per Gram)'].dtype == 'object':
            df['Price (Per Gram)'] = df['Price (Per Gram)'].str.replace('₹', '').str.replace(',', '').astype(float)
    
    # Convert Date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    return df

# Initial Data Loading
if 'data' not in st.session_state:
    raw_csv = """Date,Day,Price (Per Gram),Trend,Advice
Jan 16 2025,Thu,93.20,🔄 Steady,Base building.
Jan 17 2025,Fri,93.50,🔄 Steady,Hold.
Jan 20 2025,Mon,92.80,📉 Dip,Buy small qty.
Feb 03 2025,Mon,102.00,🚀 Budget,Duty cut impact.
Mar 07 2025,Fri,110.00,🚀 Milestone,Touched 110.
Apr 10 2025,Thu,120.00,🏆 Milestone,Crossed 120.
May 30 2025,Fri,141.20,🔥 Close,Monthly high.
Jun 19 2025,Thu,150.50,🏆 Milestone,Broken 150 barrier.
Jul 24 2025,Thu,170.00,🏆 Milestone,Crossed 170.
Sep 04 2025,Thu,200.50,🏆 HISTORIC,Crossed 2 Lakh/kg.
Oct 24 2025,Fri,240.00,🏆 Milestone,Crossed 240.
Nov 13 2025,Thu,251.00,🏆 Milestone,Quarter Million.
Jan 13 2026,Tue,307.00,🚀 ATH,All Time High."""
    
    # Using the provided data as seed
    df_initial = pd.read_csv(io.StringIO(raw_csv))
    st.session_state.data = clean_data(df_initial)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📈 Nebula Control")
    menu = st.radio("Navigation", ["Dashboard", "Price Comparison", "Advanced Lab", "Data Management"])
    st.markdown("---")
    st.info("System: Silver Tracker\nVersion: 4.0 Quantum")

# --- 1. DASHBOARD ---
if menu == "Dashboard":
    st.title("🚀 Silver Market Galaxy")
    df = st.session_state.data
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    latest_price = df['Price (Per Gram)'].iloc[-1]
    start_price = df['Price (Per Gram)'].iloc[0]
    total_growth = ((latest_price - start_price) / start_price) * 100
    
    c1.metric("Current Price", f"₹{latest_price:,.2f}")
    c2.metric("Total Growth", f"{total_growth:.1f}%", delta=f"{latest_price-start_price:.2f}")
    c3.metric("Peak Price", f"₹{df['Price (Per Gram)'].max():,.2f}")
    c4.metric("Data Points", len(df))

    # Visuals
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        fig_line = px.area(df, x='Date', y='Price (Per Gram)', 
                          title="Silver Price Trajectory (Jan 2025 - Jan 2026)",
                          line_shape="spline",
                          color_discrete_sequence=['#00d4ff'])
        fig_line.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with col_b:
        fig_pie = px.pie(df, names='Trend', title="Trend Distribution",
                        hole=0.6, color_discrete_sequence=px.colors.sequential.Electric)
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- 2. PRICE COMPARISON ---
elif menu == "Price Comparison":
    st.title("⚖️ Price Dimensional Comparison")
    df = st.session_state.data
    
    col1, col2 = st.columns(2)
    with col1:
        date_a = st.selectbox("Select Base Date", df['Date'].dt.date.unique(), index=0)
    with col2:
        date_b = st.selectbox("Select Comparison Date", df['Date'].dt.date.unique(), index=len(df)-1)
    
    row_a = df[df['Date'].dt.date == date_a].iloc[0]
    row_b = df[df['Date'].dt.date == date_b].iloc[0]
    
    comp_col1, comp_col2 = st.columns(2)
    diff = row_b['Price (Per Gram)'] - row_a['Price (Per Gram)']
    perc = (diff / row_a['Price (Per Gram)']) * 100
    
    st.write(f"### Result: {'Increase' if diff > 0 else 'Decrease'} of ₹{abs(diff):.2f} ({perc:.2f}%)")
    
    fig_comp = go.Figure(data=[
        go.Bar(name='Price', x=[str(date_a), str(date_b)], y=[row_a['Price (Per Gram)'], row_b['Price (Per Gram)']],
               marker_color=['#7b2ff7', '#00d4ff'])
    ])
    fig_comp.update_layout(template="plotly_dark", title="Price Comparison Bar")
    st.plotly_chart(fig_comp, use_container_width=True)

# --- 3. ADVANCED LAB ---
elif menu == "Advanced Lab":
    st.title("🧪 Advanced Analytics Lab")
    df = st.session_state.data
    
    st.subheader("Statistical Volatility & Moving Average")
    window = st.slider("Select Moving Average Window (Days)", 2, 20, 5)
    df['MA'] = df['Price (Per Gram)'].rolling(window=window).mean()
    
    fig_adv = go.Figure()
    fig_adv.add_trace(go.Scatter(x=df['Date'], y=df['Price (Per Gram)'], name='Actual Price', line=dict(color='#00d4ff')))
    fig_adv.add_trace(go.Scatter(x=df['Date'], y=df['MA'], name=f'{window}-Day MA', line=dict(color='#ff00ff', dash='dash')))
    
    fig_adv.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_adv, use_container_width=True)
    
    st.write("### Analysis Advice")
    st.info(f"Latest Market Intelligence: {df['Advice'].iloc[-1]}")

# --- 4. DATA MANAGEMENT ---
elif menu == "Data Management":
    st.title("📁 File Management System")
    
    # Add New Data
    with st.expander("➕ Inject New Data Entry"):
        with st.form("new_entry"):
            c1, c2, c3 = st.columns(3)
            n_date = c1.date_input("Date")
            n_price = c2.number_input("Price (₹)", min_value=0.0, format="%.2f")
            n_day = n_date.strftime("%a")
            
            c4, c5 = st.columns(2)
            n_trend = c4.selectbox("Trend", ["📈 Rising", "📉 Dip", "🔄 Steady", "🚀 Surge", "🔥 Hot"])
            n_advice = c5.text_input("Advice", "Market observation.")
            
            if st.form_submit_button("Launch into System"):
                new_row = pd.DataFrame([{
                    "Date": pd.to_datetime(n_date), "Day": n_day, 
                    "Price (Per Gram)": n_price, "Trend": n_trend, "Advice": n_advice
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.success("Data Record Synced!")

    # Bulk Upload
    with st.expander("📂 Bulk Upload CSV"):
        uploaded_file = st.file_uploader("Upload Galaxy Data CSV", type="csv")
        if uploaded_file:
            up_df = pd.read_csv(uploaded_file)
            st.session_state.data = clean_data(up_df)
            st.success("Mainframe Updated via File!")

    # Current Ledger
    st.write("### Master Ledger")
    st.dataframe(st.session_state.data.sort_values('Date', ascending=False), use_container_width=True)
    
    # Download
    csv_download = st.session_state.data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Database", data=csv_download, file_name="silver_data_export.csv", mime="text/csv")
