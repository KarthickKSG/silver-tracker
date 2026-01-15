import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Nebula Data Analytics", page_icon="🌌", layout="wide")

# --- GALAXY CUSTOM CSS (The "Galaxy" Theme) ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #16213e, #0f3460);
        color: #e94560;
    }
    
    /* Card/Container styling */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
    }

    /* Titles and Text */
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 0 0 10px #00d4ff;
        font-family: 'Orbitron', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 52, 96, 0.8);
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white;
        border-radius: 20px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #00d4ff;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
SHEET_ID = "1Qk8U4Gx4Zxxb-sTYeCSnMbCz31a2WJiLUMYIsjAcTDY"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def load_initial_data():
    df = pd.read_csv(URL)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

# Using Session State to keep data persistent during the web session
if 'main_df' not in st.session_state:
    st.session_state.main_df = load_initial_data()

df = st.session_state.main_df

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1146/1146386.png", width=100)
    st.title("Galaxy Control")
    page = st.radio("Navigate Systems", ["Live Dashboard", "Comparison Engine", "Data Laboratory", "File Management"])
    
    st.markdown("---")
    st.info("System Status: Online 🚀")

# --- PAGE 1: LIVE DASHBOARD ---
if page == "Live Dashboard":
    st.title("🌌 Cosmic Sales Intelligence")
    
    # TOP ROW KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Galaxy Sales", f"${df['Sales'].sum():,.0f}")
    kpi2.metric("Net Profit", f"${df['Profit'].sum():,.0f}")
    kpi3.metric("Total Shipments", f"{len(df):,}")
    kpi4.metric("Avg Discount", f"{df['Discount'].mean()*100:.1f}%")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Advanced Time Series
        df_ts = df.groupby('Order Date')[['Sales', 'Profit']].sum().reset_index()
        fig_ts = px.line(df_ts, x='Order Date', y=['Sales', 'Profit'], 
                        title="Sales & Profit Trajectory",
                        color_discrete_sequence=['#00d4ff', '#e94560'])
        fig_ts.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ts, use_container_width=True)

    with col2:
        # Category breakdown
        fig_cat = px.pie(df, values='Sales', names='Category', hole=0.6,
                        title="Revenue by Category",
                        color_discrete_sequence=px.colors.sequential.Electric)
        fig_cat.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_cat, use_container_width=True)

# --- PAGE 2: COMPARISON ENGINE ---
elif page == "Comparison Engine":
    st.title("⚖️ Dimensional Comparison")
    
    c1, c2 = st.columns(2)
    with c1:
        reg1 = st.selectbox("Select Dimension A (Region)", df['Region'].unique(), index=0)
    with c2:
        reg2 = st.selectbox("Select Dimension B (Region)", df['Region'].unique(), index=1)
    
    comp_df = df[df['Region'].isin([reg1, reg2])]
    
    fig_comp = px.bar(comp_df, x='Category', y='Sales', color='Region', barmode='group',
                     title=f"Performance Matrix: {reg1} vs {reg2}",
                     color_discrete_map={reg1: '#00d4ff', reg2: '#e94560'})
    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

# --- PAGE 3: DATA LABORATORY (Add New Data) ---
elif page == "Data Laboratory":
    st.title("🧪 Quantum Data Entry")
    
    with st.expander("➕ Inject New Data Record", expanded=True):
        with st.form("new_data"):
            col1, col2, col3 = st.columns(3)
            order_id = col1.text_input("Order ID", value="CA-2024-XXXX")
            date = col2.date_input("Order Date", datetime.now())
            cust = col3.text_input("Customer Name")
            
            col4, col5, col6 = st.columns(3)
            cat = col4.selectbox("Category", df['Category'].unique())
            sales = col5.number_input("Sales Amount", min_value=0.0)
            profit = col6.number_input("Profit Amount")
            
            submit = st.form_submit_button("Sync to Dashboard")
            
            if submit:
                new_entry = pd.DataFrame([{
                    "Order ID": order_id, "Order Date": pd.to_datetime(date),
                    "Customer Name": cust, "Category": cat, "Sales": sales, "Profit": profit,
                    "Region": "Central" # Default
                }])
                st.session_state.main_df = pd.concat([df, new_entry], ignore_index=True)
                st.success("Data Record Synced successfully!")
                st.balloons()

# --- PAGE 4: FILE MANAGEMENT ---
elif page == "File Management":
    st.title("📁 Archive Management")
    
    st.write("### Current Ledger")
    st.dataframe(df.sort_values(by='Order Date', ascending=False), use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Export Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV Archive", data=csv, file_name="galaxy_data.csv", mime="text/csv")
        
    with col2:
        st.write("### Bulk Import")
        uploaded_file = st.file_uploader("Upload New Sales Data (CSV)")
        if uploaded_file:
            new_df = pd.read_csv(uploaded_file)
            st.session_state.main_df = pd.concat([df, new_df], ignore_index=True)
            st.success("Bulk Upload Complete!")
