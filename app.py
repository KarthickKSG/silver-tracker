import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="Nebula Quantum Analytics", page_icon="📈", layout="wide")

# --- ADVANCED GALAXY CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }

    /* Glassmorphism Cards */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
    }

    /* Neon Accents */
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #7b2ff7);
        color: white; border-radius: 12px; border: none;
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00d4ff;
        transform: translateY(-2px);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 30, 0.95);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORE DATA ENGINE ---
def process_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Clean columns
        df.columns = [str(c).strip() for c in df.columns]
        
        # Clean Price column (handles ₹, commas)
        price_col = [c for c in df.columns if 'Price' in c or 'price' in c][0]
        if df[price_col].dtype == 'object':
            df[price_col] = df[price_col].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        
        # Clean Date column
        date_col = [c for c in df.columns if 'Date' in c or 'date' in c][0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col, price_col]).sort_values(date_col)
        
        return df, date_col, price_col
    except Exception as e:
        st.error(f"Mapping Error: {e}")
        return None, None, None

# --- INITIAL DATA STATE ---
if 'data_1' not in st.session_state:
    st.session_state.data_1 = None
if 'data_2' not in st.session_state:
    st.session_state.data_2 = None

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2022/2022299.png", width=80)
    st.title("Nebula Control")
    mode = st.radio("System Mode", ["Overview Analytics", "Dual CSV Compare", "Data Management"])
    
    st.markdown("---")
    st.subheader("📁 Upload Data")
    file1 = st.file_uploader("Primary CSV (Required)", type="csv")
    if file1:
        st.session_state.data_1, d1, p1 = process_csv(file1)
        
    file2 = st.file_uploader("Secondary CSV (Optional Comparison)", type="csv")
    if file2:
        st.session_state.data_2, d2, p2 = process_csv(file2)

# --- MAIN LOGIC ---
if st.session_state.data_1 is not None:
    df1 = st.session_state.data_1
    d_col, p_col = "Date", "Price (Per Gram)" # Standardized names from process_csv

    # --- 1. OVERVIEW ANALYTICS ---
    if mode == "Overview Analytics":
        st.title("🚀 Galaxy Data Intelligence")
        
        # Filtering System
        with st.expander("🔍 Advanced Filtering Laboratory"):
            c1, c2, c3 = st.columns(3)
            min_date = df1[d_col].min().date()
            max_date = df1[d_col].max().date()
            date_range = c1.date_input("Time Window", [min_date, max_date])
            
            trend_filter = c2.multiselect("Filter by Trend", df1['Trend'].unique() if 'Trend' in df1.columns else [])
            price_limit = c3.slider("Price Threshold (Min)", float(df1[p_col].min()), float(df1[p_col].max()))

            # Apply Filters
            mask = (df1[d_col].dt.date >= date_range[0]) & (df1[d_col].dt.date <= date_range[1])
            if trend_filter:
                mask = mask & (df1['Trend'].isin(trend_filter))
            mask = mask & (df1[p_col] >= price_limit)
            filtered_df = df1[mask]

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        current = filtered_df[p_col].iloc[-1]
        start = filtered_df[p_col].iloc[0]
        change = ((current - start) / start) * 100
        
        k1.metric("Current Price", f"₹{current:,.2f}", f"{change:.1f}%")
        k2.metric("Market Peak", f"₹{filtered_df[p_col].max():,.2f}")
        k3.metric("Volatility (Std)", f"{filtered_df[p_col].std():.2f}")
        k4.metric("Data Points", len(filtered_df))

        # Charts Row 1
        col_main, col_dist = st.columns([2, 1])
        
        with col_main:
            # Multi-Layer Price Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=filtered_df[d_col], y=filtered_df[p_col], 
                                     name="Spot Price", fill='tozeroy',
                                     line=dict(color='#00d4ff', width=3)))
            # Moving Average
            filtered_df['MA7'] = filtered_df[p_col].rolling(7).mean()
            fig.add_trace(go.Scatter(x=filtered_df[d_col], y=filtered_df['MA7'], 
                                     name="7-Day Avg", line=dict(color='#ff00ff', dash='dot')))
            
            fig.update_layout(template="plotly_dark", title="Quantum Price Trajectory",
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'))
            st.plotly_chart(fig, use_container_width=True)

        with col_dist:
            # Volatility Analysis
            fig_box = px.violin(filtered_df, y=p_col, box=True, points="all",
                               title="Price Density Distribution", color_discrete_sequence=['#7b2ff7'])
            fig_box.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_box, use_container_width=True)

        # Charts Row 2
        st.write("### 🧪 Trend & Behavioral Labs")
        c_a, c_b = st.columns(2)
        
        with c_a:
            if 'Trend' in filtered_df.columns:
                fig_bar = px.bar(filtered_df.groupby('Trend').size().reset_index(name='count'), 
                                x='Trend', y='count', color='Trend', title="Market Sentiment Frequency")
                fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with c_b:
            filtered_df['Returns'] = filtered_df[p_col].pct_change() * 100
            fig_ret = px.histogram(filtered_df, x='Returns', title="Daily Returns % (Volatility)",
                                  color_discrete_sequence=['#00d4ff'], nbins=30)
            fig_ret.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_ret, use_container_width=True)

    # --- 2. DUAL CSV COMPARE ---
    elif mode == "Dual CSV Compare":
        st.title("⚖️ Dimensional Comparison Engine")
        
        if st.session_state.data_2 is not None:
            df2 = st.session_state.data_2
            
            col_left, col_right = st.columns(2)
            col_left.metric("Dataset 1 Max", f"₹{df1[p_col].max():,.2f}")
            col_right.metric("Dataset 2 Max", f"₹{df2[p_col].max():,.2f}")
            
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(x=df1[d_col], y=df1[p_col], name="Primary Dataset", line=dict(color='#00d4ff')))
            fig_comp.add_trace(go.Scatter(x=df2[d_col], y=df2[p_col], name="Secondary Dataset", line=dict(color='#ff00ff')))
            
            fig_comp.update_layout(template="plotly_dark", title="Overlay Performance Analysis",
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Statistics Table
            st.write("### Comparative Statistics")
            stats = pd.DataFrame({
                "Metric": ["Average", "Min", "Max", "Growth"],
                "Primary": [df1[p_col].mean(), df1[p_col].min(), df1[p_col].max(), df1[p_col].iloc[-1] - df1[p_col].iloc[0]],
                "Secondary": [df2[p_col].mean(), df2[p_col].min(), df2[p_col].max(), df2[p_col].iloc[-1] - df2[p_col].iloc[0]]
            })
            st.table(stats)
        else:
            st.warning("Please upload a second CSV in the sidebar to use the Comparison Engine.")

    # --- 3. DATA MANAGEMENT ---
    elif mode == "Data Management":
        st.title("📁 File Management & Ledger")
        
        tab1, tab2 = st.tabs(["Add Entry", "Raw Data Archive"])
        
        with tab1:
            with st.form("manual_input"):
                c1, c2, c3 = st.columns(3)
                new_date = c1.date_input("Entry Date")
                new_price = c2.number_input("Price Value", min_value=0.0)
                new_trend = c3.selectbox("Trend", ["📈 Rising", "📉 Dip", "🔄 Steady", "🚀 Surge"])
                
                if st.form_submit_button("Sync to Cloud"):
                    new_row = pd.DataFrame([{d_col: pd.to_datetime(new_date), p_col: new_price, 'Trend': new_trend}])
                    st.session_state.data_1 = pd.concat([st.session_state.data_1, new_row], ignore_index=True).sort_values(d_col)
                    st.success("Record Synced!")
                    st.rerun()

        with tab2:
            st.dataframe(df1.sort_values(d_col, ascending=False), use_container_width=True)
            csv = df1.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Master Ledger", data=csv, file_name="master_silver_data.csv", mime="text/csv")

else:
    # Landing Page
    st.title("🌌 Welcome to Nebula Quantum")
    st.info("Please upload a Silver Price CSV file in the sidebar to activate the galaxy mainframe.")
    st.write("### Expected CSV Format:")
    st.code("Date, Price (Per Gram), Trend, Advice\nJan 16 2025, 93.20, 🔄 Steady, Base building.")
