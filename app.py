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
        background: radial-gradient(circle at top right, #0a0a12, #16213e, #0f3460);
        color: #ffffff;
    }
    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        text-shadow: 0 0 10px #00d4ff;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white; border-radius: 20px; border: none;
    }
    /* Glassmorphism style cards */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE (TARGETING THE 'ORDERS' SHEET) ---
# We use GID=0 which is usually the 'Orders' sheet in this specific dataset
SHEET_ID = "1Qk8U4Gx4Zxxb-sTYeCSnMbCz31a2WJiLUMYIsjAcTDY"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=600)
def load_and_clean_data():
    try:
        df = pd.read_csv(URL)
        
        # 1. Clean Column Names (Remove spaces and make Title Case)
        df.columns = [str(col).strip() for col in df.columns]
        
        # 2. Smart Column Detection (In case names are lowercase or slightly different)
        column_map = {
            'sales': 'Sales',
            'profit': 'Profit',
            'category': 'Category',
            'region': 'Region',
            'order date': 'Order Date',
            'discount': 'Discount'
        }
        
        # Rename columns to standard names for our app
        for actual_col in df.columns:
            if actual_col.lower() in column_map:
                df.rename(columns={actual_col: column_map[actual_col.lower()]}, inplace=True)

        # 3. Data Type Fixes
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        
        numeric_cols = ['Sales', 'Profit', 'Discount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df
    except Exception as e:
        st.error(f"Galaxy Connection Failed: {e}")
        return pd.DataFrame()

# Initialize session state for persistence
if 'main_df' not in st.session_state:
    st.session_state.main_df = load_and_clean_data()

df = st.session_state.main_df

# --- VALIDATION ---
required = ['Sales', 'Profit', 'Category']
found = [c for c in required if c in df.columns]

if len(found) < len(required):
    st.error("❌ Critical Error: Data mapping failed.")
    st.write(f"I found {found}, but I need {required}.")
    st.write("Here is what your sheet looks like to me right now:")
    st.dataframe(df.head(5))
    st.info("Check if the first sheet in your Google Sheets file is actually the data sheet.")
    st.stop()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🌌 Nebula Admin")
    page = st.radio("Navigation", ["Overview Dashboard", "Market Comparison", "Record Management"])
    st.markdown("---")
    if st.button("🔄 Sync with Google Cloud"):
        st.session_state.main_df = load_and_clean_data()
        st.success("Synced!")
        st.rerun()

# --- DASHBOARD PAGE ---
if page == "Overview Dashboard":
    st.title("🚀 Cosmic Sales Overview")
    
    # KPI ROLLS
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Revenue", f"${df['Sales'].sum():,.0f}")
    k2.metric("Net Profit", f"${df['Profit'].sum():,.0f}")
    k3.metric("Total Orders", f"{len(df):,}")
    k4.metric("Margin", f"{(df['Profit'].sum()/df['Sales'].sum()*100):.1f}%")

    # CHARTS
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Sales Trend
        trend_df = df.groupby(df['Order Date'].dt.date)['Sales'].sum().reset_index()
        fig_trend = px.area(trend_df, x='Order Date', y='Sales', title="Revenue Trajectory",
                           color_discrete_sequence=['#00d4ff'])
        fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        # Category Pie
        fig_pie = px.pie(df, values='Sales', names='Category', hole=0.5, title="Category Mix")
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- COMPARISON PAGE ---
elif page == "Market Comparison":
    st.title("⚖️ Dimensional Analysis")
    
    compare_dim = st.selectbox("Select Dimension to Compare", ["Region", "Segment", "Category"])
    
    vals = df[compare_dim].unique()
    c1, c2 = st.columns(2)
    dim_a = c1.selectbox("Dimension A", vals, index=0)
    dim_b = c2.selectbox("Dimension B", vals, index=1 if len(vals)>1 else 0)
    
    comp_df = df[df[compare_dim].isin([dim_a, dim_b])]
    fig_comp = px.bar(comp_df, x='Category', y='Sales', color=compare_dim, barmode='group',
                     title=f"Head-to-Head: {dim_a} vs {dim_b}")
    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

# --- RECORD MANAGEMENT PAGE ---
elif page == "Record Management":
    st.title("📁 File & Record Management")
    
    # Tabbed Management
    tab1, tab2 = st.tabs(["Manual Entry", "Database View"])
    
    with tab1:
        with st.form("manual_entry"):
            st.subheader("Inject New Order")
            col1, col2, col3 = st.columns(3)
            oid = col1.text_input("Order ID", "NEW-12345")
            osales = col2.number_input("Sales", min_value=0.0)
            oprofit = col3.number_input("Profit")
            
            col4, col5 = st.columns(2)
            ocat = col4.selectbox("Category", df['Category'].unique())
            oreg = col5.selectbox("Region", df['Region'].unique())
            
            if st.form_submit_button("Launch to Database"):
                new_row = pd.DataFrame([{
                    "Order ID": oid, "Sales": osales, "Profit": oprofit,
                    "Category": ocat, "Region": oreg, "Order Date": datetime.now()
                }])
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_row], ignore_index=True)
                st.success("New record synchronized successfully!")

    with tab2:
        st.write("### Current Ledger")
        st.dataframe(st.session_state.main_df.sort_values(by='Order Date', ascending=False), use_container_width=True)
        
        csv = st.session_state.main_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Galaxy Archive (CSV)", data=csv, file_name="galaxy_data.csv")
