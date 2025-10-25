import streamlit as st
import pandas as pd
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="USDBased & CoinBased Trading Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Trading Strategy Data Analytics Dashboard")
st.divider()  # Cleaner separator

# --- 2. Data Loading & Processing Functions ---
def load_data(data_type, base_type):
    """
    Load and process data based on file naming and column conventions.
    
    Parameters:
    data_type (str): Type of data, e.g., 'PnL', 'Volume', 'Fee', 'Funding'
    base_type (str): Denomination type, e.g., 'USDBased', 'CoinBased'
    
    Returns:
    pd.DataFrame: DataFrame with date index and selected data column. 
                  Returns None if file doesn't exist.
    """
    # Construct filename (assuming date range: 20250407 - 20251021)
    file_name = f"{data_type} - ETH - {base_type} - Records - 20250407 - 20251021.csv"
    
    # Check file existence
    if not os.path.exists(file_name):
        st.sidebar.error(f"🚨 File missing: {file_name} not found")
        return None
    
    try:
        df = pd.read_csv(file_name)
        st.sidebar.caption(f"Loaded: {file_name}")
        
        # 1. Standardize date column
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        # 2. Select core columns based on data type
        df.columns = df.columns.str.strip()  # Clean column names
        selected_col = None
        
        if data_type in ['PnL', 'Fee', 'Funding']:
            # Prioritize cumulative trends for these metrics
            cumulative_cols = [col for col in df.columns 
                             if 'Cumulative' in col or 'CUMULATIVE' in col]
            if cumulative_cols:
                selected_col = cumulative_cols[0]
                new_col_name = f'{data_type} Cumulative'
            else:
                # Fallback to daily values if no cumulative data
                daily_cols = [col for col in df.columns 
                            if 'Daily' in col or 'DAILY' in col]
                if daily_cols:
                    selected_col = daily_cols[0]
                    new_col_name = f'{data_type} Daily'
                else:
                    st.warning(f"⚠️ No 'Cumulative' or 'Daily' columns found in {file_name}")
                    return None
        
        elif data_type == 'Volume':
            # Volume typically uses daily values
            daily_cols = [col for col in df.columns 
                        if 'Daily' in col or 'DAILY' in col]
            if daily_cols:
                selected_col = daily_cols[0]
                new_col_name = f'{data_type} Daily'
            else:
                st.warning(f"⚠️ No 'Daily' columns found in {file_name}")
                return None
        
        # Prepare final DataFrame
        if selected_col:
            df = df[[selected_col]].rename(columns={selected_col: new_col_name})
            df = df.dropna()  # Remove missing values for smoother plotting
            return df
        else:
            return None
            
    except Exception as e:
        st.error(f"Error processing {file_name}: {str(e)}")
        return None

# --- 3. Visualization Components ---
def display_data_block(title, df, unit=""):
    """Display data with metrics, chart, and raw data expander"""
    if df is None or df.empty:
        st.info(f"No data available for {title}.")
        return
    
    # Card-style container for better visual grouping
    with st.container(border=True):
        # Title with subtle icon
        st.subheader(title)
        
        # Key metric: Latest value
        col_name = df.columns[0]
        latest_value = df[col_name].iloc[-1]
        
        # Format based on metric type
        format_str = ".2f" if "Cumulative" in col_name else ".4f"
        st.metric(
            label=f"Latest {col_name}",
            value=f"{latest_value:{format_str}} {unit}"
        )
        
        # Interactive line chart
        st.line_chart(df, use_container_width=True, height=250)
        
        # Raw data expander (collapsed by default)
        with st.expander("📝 View recent raw data", expanded=False):
            st.dataframe(df.tail(7), use_container_width=True)

# --- 4. Dashboard Main Layout ---
# Data type mapping for display names
data_map = {
    "PnL": "Profit and Loss (PnL)",
    "Volume": "Trading Volume (Volume)",
    "Fee": "Transaction Fees (Fee)",
    "Funding": "Funding Costs (Funding)"
}

# --------------------------
# A. USDBased - USD Denominated Data
# --------------------------
st.header("💵 USDBased - USD Denominated Data")
st.divider()

# PnL Section (prominent top position)
display_data_block(f"📈 {data_map['PnL']}", 
                  load_data("PnL", "USDBased"), 
                  unit="$")

st.write("")  # Spacer

# Secondary metrics in 3-column grid
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    display_data_block(f"💰 {data_map['Fee']}", 
                      load_data("Fee", "USDBased"), 
                      unit="$")

with col2:
    display_data_block(f"💸 {data_map['Funding']}", 
                      load_data("Funding", "USDBased"), 
                      unit="$")

with col3:
    display_data_block(f"📊 {data_map['Volume']}", 
                      load_data("Volume", "USDBased"), 
                      unit="$")

# Vertical spacer between sections
st.markdown("---")
st.write("")

# --------------------------
# B. CoinBased - Coin Denominated Data
# --------------------------
st.header("🪙 CoinBased - Coin Denominated Data")
st.divider()

# PnL Section (prominent top position)
display_data_block(f"📈 {data_map['PnL']}", 
                  load_data("PnL", "CoinBased"), 
                  unit="ETH")

st.write("")  # Spacer

# Secondary metrics in 3-column grid
col4, col5, col6 = st.columns(3, gap="medium")

with col4:
    display_data_block(f"💰 {data_map['Fee']}", 
                      load_data("Fee", "CoinBased"), 
                      unit="ETH")

with col5:
    display_data_block(f"💸 {data_map['Funding']}", 
                      load_data("Funding", "CoinBased"), 
                      unit="ETH")

with col6:
    display_data_block(f"📊 {data_map['Volume']}", 
                      load_data("Volume", "CoinBased"), 
                      unit="ETH")