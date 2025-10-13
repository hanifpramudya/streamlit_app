import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Risk Management Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    header {
        visibility: visible !important;
    }
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-table {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .summary-box {
        background-color: #e8e8e8;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .survey-card {
        background-color: white;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 8px;
    }
    .grc-card {
        background-color: white;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 8px;
    }
    .grc-number {
        font-size: 32px;
        color: #ff6347;
        font-weight: bold;
        margin: 5px 0;
    }
    .survey-number {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin: 5px 0;
    }
    .survey-label {
        color: #999;
        font-size: 12px;
    }
    h1 {
        font-size: 28px !important;
        margin-bottom: 0.5rem !important;
        padding: 0 !important;
    }
    h3 {
        font-size: 18px !important;
        margin: 0.5rem 0 !important;
    }
    h4 {
        font-size: 14px !important;
        margin: 0.3rem 0 !important;
    }
    .stButton button {
        width: 100%;
        height: 35px;
        padding: 5px;
        font-size: 13px;
    }
    div[data-testid="stSelectbox"] {
        margin-bottom: 0.5rem;
    }
    .element-container {
        margin-bottom: 0.3rem;
    }
    [data-testid="stTextArea"] textarea {
        height: 100px !important;
        min-height: 100px !important;
    }
    .nav-button {
        background-color: #20B2AA;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'menu'
if 'df_ytd' not in st.session_state:
    st.session_state.df_ytd = None
if 'df_summary' not in st.session_state:
    st.session_state.df_summary = None
if 'df_summary_present' not in st.session_state:
    st.session_state.df_summary_present = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'latest_col_ytd_idx' not in st.session_state:
    st.session_state.latest_col_ytd_idx = None
if 'latest_col_idx' not in st.session_state:
    st.session_state.latest_col_idx = None

def process_excel_data(uploaded_file):
    """Process Excel file and return cleaned dataframes"""
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        
        # Process Data_YTD sheet
        df_ytd = None
        latest_col_ytd_idx = None
        if "Data_YTD" in excel_file.sheet_names:
            df_ytd = pd.read_excel(uploaded_file, sheet_name="Data_YTD")
            
            if 'Unnamed: 0' in df_ytd.columns:
                df_ytd = df_ytd.drop('Unnamed: 0', axis=1)
            if 'Unnamed: 1' in df_ytd.columns:
                df_ytd = df_ytd.rename(columns={'Unnamed: 1': 'Parameter'})
            
            cols = list(df_ytd.columns)
            new_cols = []
            last_named = None
            
            for col in cols:
                col_str = str(col)
                if col_str.startswith('Unnamed: '):
                    new_cols.append(last_named if last_named else col)
                else:
                    new_cols.append(col)
                    if col != 'Parameter':
                        last_named = col
            
            df_ytd.columns = new_cols
            
            if len(df_ytd) > 0:
                df_ytd.iloc[0] = df_ytd.iloc[0].ffill()
            
            if len(df_ytd) > 0:
                new_columns = []
                for i, col in enumerate(df_ytd.columns):
                    if col == 'Parameter':
                        new_columns.append('Parameter')
                    else:
                        row_0_value = str(df_ytd.iloc[0, i]) if pd.notna(df_ytd.iloc[0, i]) else ''
                        new_columns.append(f"{row_0_value}-{col}")
                
                df_ytd.columns = new_columns
                df_ytd = df_ytd.iloc[1:].reset_index(drop=True)

                df_ytd_numpy = df_ytd.to_numpy()
                row_0_ytd_numpy = df_ytd_numpy[0]
                nan_indices = int(np.where(pd.isna(row_0_ytd_numpy))[0][0])
                latest_col_ytd_idx = df_ytd.columns[nan_indices-1]
                present_col_ytd = df_ytd.columns[max(0, nan_indices - 13):nan_indices]

        # Process Summary sheet
        df_summary = None
        df_summary_present = None
        latest_col_idx = None
        
        if "Summary" in excel_file.sheet_names:
            df_summary = pd.read_excel(uploaded_file, sheet_name="Summary")
            
            original_columns = df_summary.columns.tolist()
            df_summary.loc[-1] = original_columns
            df_summary.index = df_summary.index + 1
            df_summary = df_summary.sort_index()
            
            df_summary.columns = [f'Col_{i}' for i in range(len(df_summary.columns))]
            df_summary = df_summary.drop('Col_0', axis=1)
            df_summary = df_summary.rename(columns={'Col_1': 'Parameter'})
            df_summary = df_summary.iloc[1:].reset_index(drop=True)
            
            if len(df_summary) > 0:
                df_summary.iloc[0] = df_summary.iloc[0].ffill()
            
            if len(df_summary) > 1:
                first_nan = True
                for i in range(2, len(df_summary.columns)):
                    col = df_summary.columns[i]
                    if col != 'Parameter' and pd.isna(df_summary.iloc[1, i]):
                        left_col = df_summary.columns[i-1]
                        left_value = str(df_summary.iloc[1, df_summary.columns.get_loc(left_col)])
                        
                        if first_nan:
                            df_summary.iloc[1, i] = f"{left_value}-weighted"
                            first_nan = False
                        else:
                            df_summary.iloc[1, i] = f"{left_value}-score classification"
                            first_nan = True
            
            if len(df_summary) > 1:
                new_columns = []
                for i, col in enumerate(df_summary.columns):
                    row_0_value = str(df_summary.iloc[0, i]) if pd.notna(df_summary.iloc[0, i]) else ''
                    row_1_value = str(df_summary.iloc[1, i]) if pd.notna(df_summary.iloc[1, i]) else ''
                    
                    if i < 2:
                        new_columns.append(f"{row_0_value}")
                    else:
                        if 'weighted' in row_1_value.lower() or 'weighted-classification' in row_1_value.lower():
                            row_1_parts = row_1_value.split('-')
                            if len(row_1_parts) >= 3:
                                try:
                                    result = f"{row_1_parts[0]}-{row_0_value}-{row_1_parts[1]}-{row_1_parts[2]}"
                                except:
                                    result = f"{row_0_value}-{row_1_parts[1]}"
                                new_columns.append(result)
                            elif len(row_1_parts) >= 2:
                                new_columns.append(f"{row_1_parts[0]}-{row_0_value}-{row_1_parts[1]}")
                            else:
                                new_columns.append(f"{row_1_value}-{row_0_value}")
                        else:
                            new_columns.append(f"{row_1_value}-{row_0_value}")
                
                df_summary.columns = new_columns
                df_summary = df_summary.iloc[2:].reset_index(drop=True)
            
            if len(df_summary) > 0:
                date_columns = [col for col in df_summary.columns if col not in ['Parameter', 'nan-nan']]
                
                if len(date_columns) >= 2:
                    df_numpy = df_summary.to_numpy()
                    row_0_numpy = df_numpy[0]
                    nan_mask = row_0_numpy == '-'
                    if nan_mask.any():
                        nan_indices = int(np.where(nan_mask)[0][0])
                        latest_col_idx = nan_indices - 3
                        previous_col_idx = nan_indices - 6

                        if previous_col_idx >= 0 and latest_col_idx >= 0:
                            latest_col = df_summary.columns[latest_col_idx]
                            previous_col = df_summary.columns[previous_col_idx]

                            # Check if 'Jenis Risiko' column exists
                            if 'Jenis Risiko' in df_summary.columns:
                                df_summary_present = df_summary[['Jenis Risiko', previous_col, latest_col]].copy()
                                df_summary_present.columns = ['Kategori Risiko', 'previous_month', 'present_month']
                            else:
                                # Use first column as risk category
                                df_summary_present = df_summary.iloc[:, [0, previous_col_idx, latest_col_idx]].copy()
                                df_summary_present.columns = ['Kategori Risiko', 'previous_month', 'present_month']
        
        return df_ytd, df_summary, df_summary_present, latest_col_idx, latest_col_ytd_idx, True, "Data processed successfully!"
    
    except Exception as e:
        return None, None, None, None, None, False, f"Error processing file: {str(e)}"

def show_data_upload():
    """Display data upload interface"""
    st.title("📊 Excel File Upload and Display")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        df_ytd, df_summary, df_summary_present, latest_col_idx, latest_col_ytd_idx, success, message = process_excel_data(uploaded_file)
        
        if success:
            st.success(f"✅ {message}")
            
            # Store in session state
            st.session_state.df_ytd = df_ytd
            st.session_state.df_summary = df_summary
            st.session_state.df_summary_present = df_summary_present
            st.session_state.latest_col_idx = latest_col_idx
            st.session_state.latest_col_ytd_idx = latest_col_ytd_idx
            st.session_state.uploaded_file = uploaded_file
            
            # Display preview
            if df_ytd is not None:
                st.header("📈 Data_YTD Preview")
                st.dataframe(df_ytd.head(10), use_container_width=True)
            
            if df_summary_present is not None:
                st.header("📊 Summary Preview")
                st.dataframe(df_summary_present, use_container_width=True)
            
            st.divider()
            if st.button("✅ Confirm and View Dashboard", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
        else:
            st.error(f"❌ {message}")
    else:
        st.info("👆 Please upload an Excel file to get started")
        st.write("**Note:** The file should contain sheets named 'Data_YTD' and 'Summary'")

def show_dashboard():
    """Display the risk management dashboard"""
    
    # Check if data is loaded
    if st.session_state.df_summary is None or st.session_state.df_summary_present is None:
        st.error("No data loaded. Please upload data first.")
        return
    
    # Initialize variables
    df_numpy = st.session_state.df_summary.to_numpy()
    row_0_numpy = df_numpy[0]
    nan_mask = row_0_numpy == '-'
    
    if nan_mask.any():
        nan_indices = int(np.where(nan_mask)[0][0])
        latest_col_idx = nan_indices - 3
    else:
        latest_col_idx = st.session_state.latest_col_idx if st.session_state.latest_col_idx else len(st.session_state.df_summary.columns) - 1
    
    # Get latest_col_ytd_idx from session state or calculate
    if st.session_state.latest_col_ytd_idx:
        latest_col_ytd_idx = st.session_state.latest_col_ytd_idx
    else:
        latest_col_ytd_idx = None

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Risk Management Dashboard")
    with col2:
        try:
            st.image("Logo.png", width = 250)
        except:
            st.write("🏢")
    
    # Date selector
    date_col1, date_col2 = st.columns([1, 5])
    with date_col1:
        if latest_col_ytd_idx and st.session_state.df_ytd is not None:
            # Get columns up to latest_col_ytd_idx, excluding 'Parameter'
            col_position = st.session_state.df_ytd.columns.get_loc(latest_col_ytd_idx)
            available_dates = [col for col in st.session_state.df_ytd.columns[:col_position + 1] if col != 'Parameter']
            if available_dates:
                selected_date = st.selectbox(
                    "Select Date",
                    options=available_dates,
                    index=len(available_dates) - 1
                )
            else:
                st.warning("No dates available")
        else:
            st.warning("No dates available")

    # Summary Section
    st.markdown("### Summary")
    
    col_summary, col_nps, col_legend = st.columns([3, 2, 1.2])
    
    with col_summary:
        st.markdown('<div class="risk-table">', unsafe_allow_html=True)
        
        if st.session_state.df_summary_present is not None:
            def color_cells(val):
                try:
                    val_float = float(val)
                    if val_float <= 1.79:
                        return 'background-color: #90d050'
                    elif val_float <= 2.59:
                        return 'background-color: #fff2cc'
                    elif val_float <= 3.39:
                        return 'background-color: #ffff00'
                    elif val_float <= 4.19:
                        return 'background-color: #ffc001'
                    elif val_float <= 5:
                        return 'background-color: #ff0000'
                    else:
                        return ''
                except:
                    return ''
            
            styled_df = st.session_state.df_summary_present[:9].style.map(
                color_cells, 
                subset=['previous_month', 'present_month']
            )
            st.dataframe(styled_df, hide_index=True, use_container_width=True, height=350)
        else:
            st.warning("No data available. Please upload data first.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_nps:
        st.markdown("#### Composite score")
        st.markdown("")
        
        # Safely get the composite score
        try:
            composite_score = float(st.session_state.df_summary_present['present_month'].iloc[10])
        except:
            composite_score = 0.0
        
        st.markdown(f"<p style='text-align: center;'><strong>Average Risk</strong><br>NPS Score is {composite_score:.2f}</p>", unsafe_allow_html=True)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=composite_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 32}},
            gauge={
                'axis': {'range': [None, 5], 'tickwidth': 2},
                'bar': {'color': "black", 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'steps': [
                    {'range': [0, 1.80], 'color': '#90d050'},
                    {'range': [1.80, 2.60], 'color': '#fff2cc'},
                    {'range': [2.60, 3.40], 'color': '#ffff00'},
                    {'range': [3.40, 4.20], 'color': '#ffc001'},
                    {'range': [4.20, 5], 'color': '#ff0000'}
                ],
            }
        ))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=0, b=20))
        st.plotly_chart(fig, use_container_width=True, key="nps_gauge")
    
    with col_legend:
        with st.container(border=True):
            st.markdown("#### Legend")
            st.markdown('<span style="color: #90d050; font-size: 20px;">●</span> Low', unsafe_allow_html=True)
            st.markdown('<span style="color: #fff2cc; font-size: 20px;">●</span> Low to Moderate', unsafe_allow_html=True)
            st.markdown('<span style="color: #ffff00; font-size: 20px;">●</span> Moderate', unsafe_allow_html=True)
            st.markdown('<span style="color: #ffc001; font-size: 20px;">●</span> Moderate to High', unsafe_allow_html=True)
            st.markdown('<span style="color: #ff0000; font-size: 20px;">●</span> High', unsafe_allow_html=True)
    
    # Dropdown for risk type
    risk_types = ["Keseluruhan Risiko"]
    if 'Jenis Risiko' in st.session_state.df_summary.columns:
        risk_types.extend(st.session_state.df_summary['Jenis Risiko'][:9].tolist())
    
    st.selectbox("Select Risk Type", risk_types, label_visibility="collapsed")
    
    # Survey and GRC Section
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
    
    survey_cols = [col1, col2, col3, col4, col5, col6, col7, col8]
    for i, col in enumerate(survey_cols):
        with col:
            st.markdown('<div class="survey-card">', unsafe_allow_html=True)
            st.markdown('<div class="survey-label">Survey</div>', unsafe_allow_html=True)
            st.markdown('<div class="survey-number">60</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    grc_cols = [col9, col10]
    for i, col in enumerate(grc_cols):
        with col:
            st.markdown('<div class="grc-card">', unsafe_allow_html=True)
            st.markdown('<div class="survey-label">GRC</div>', unsafe_allow_html=True)
            st.markdown('<div class="grc-number">06</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottom Section
    col_left, col_middle, col_right = st.columns([1, 2, 2])
    
    with col_left:
        st.markdown("#### Jumlah gugatan")
        st.text_area("", "", height=100, label_visibility="collapsed")
        
        st.markdown("#### Jumlah Fraud")
        st.text_area("", "", height=100, label_visibility="collapsed", key="fraud")
    
    with col_middle:
        st.button("Pilih Variabel", use_container_width=True)
        
        st.markdown("**CSAT Trend**")
        
        years = [2015, 2016, 2017, 2018, 2019, 2020]
        values = [6.0, 6.5, 6.7, 7.0, 7.3, 7.8]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=years, 
            y=values,
            mode='lines+markers',
            line=dict(color='#20B2AA', width=3),
            marker=dict(size=8, color='#20B2AA')
        ))
        
        fig_trend.update_layout(
            height=250,
            margin=dict(l=30, r=20, t=10, b=30),
            xaxis=dict(showgrid=False),
            yaxis=dict(range=[0, 8.5], showgrid=True, gridcolor='lightgray'),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True, key="csat_trend")
    
    with col_right:
        st.button("Pilih Variabel", use_container_width=True, key="var2")
        
        st.markdown("**CSAT Score**")
        
        fig_csat = go.Figure(go.Indicator(
            mode="gauge+number",
            value=8.44,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'suffix': '', 'font': {'size': 28}},
            gauge={
                'axis': {'range': [0, 10], 'tickwidth': 1},
                'bar': {'color': "white", 'thickness': 0},
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 8.44], 'color': '#20B2AA'},
                    {'range': [8.44, 10], 'color': '#E0E0E0'}
                ],
                'threshold': {
                    'line': {'color': "#20B2AA", 'width': 4},
                    'thickness': 0.75,
                    'value': 8.44
                }
            }
        ))
        fig_csat.update_layout(
            height=140,
            margin=dict(l=10, r=10, t=10, b=10),
            annotations=[
                dict(text="▲ 25.09%", x=0.5, y=0.3, showarrow=False, font=dict(size=10)),
                dict(text="Current Year - Last Year", x=0.5, y=0.15, showarrow=False, font=dict(size=8, color='gray'))
            ]
        )
        st.plotly_chart(fig_csat, use_container_width=True, key="csat_score")
        
        metrics_data = [
            ("Technical Copebilitis", "46%"),
            ("Timely Deliverie", "74%"),
            ("Quality of Deliverable", "14%"),
            ("Program Governance", "46%"),
            ("New Ideas & Creative Solution", "54%"),
            ("New Ideas & Creative Solution", "54%")
        ]
        
        metrics_cols1 = st.columns(3)
        for i in range(3):
            label, value = metrics_data[i]
            with metrics_cols1[i]:
                fig_metric = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=int(value.strip('%')),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    number={'suffix': '%', 'font': {'size': 12}},
                    gauge={
                        'axis': {'range': [0, 100], 'visible': False},
                        'bar': {'color': "white", 'thickness': 0},
                        'bgcolor': "white",
                        'borderwidth': 2.5,
                        'bordercolor': '#20B2AA',
                        'steps': [
                            {'range': [0, int(value.strip('%'))], 'color': '#20B2AA'},
                            {'range': [int(value.strip('%')), 100], 'color': '#E0E0E0'}
                        ],
                    }
                ))
                fig_metric.update_layout(
                    height=80,
                    margin=dict(l=5, r=5, t=0, b=0)
                )
                st.plotly_chart(fig_metric, use_container_width=True, key=f"metric_{i}")
                st.markdown(f"<p style='text-align: center; font-size: 9px; margin-top: -10px;'>{label}</p>", unsafe_allow_html=True)
        
        metrics_cols2 = st.columns(3)
        for i in range(3, 6):
            label, value = metrics_data[i]
            with metrics_cols2[i-3]:
                fig_metric = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=int(value.strip('%')),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    number={'suffix': '%', 'font': {'size': 12}},
                    gauge={
                        'axis': {'range': [0, 100], 'visible': False},
                        'bar': {'color': "white", 'thickness': 0},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': '#20B2AA',
                        'steps': [
                            {'range': [0, int(value.strip('%'))], 'color': '#20B2AA'},
                            {'range': [int(value.strip('%')), 100], 'color': '#E0E0E0'}
                        ],
                    }
                ))
                fig_metric.update_layout(
                    height=80,
                    margin=dict(l=5, r=5, t=0, b=0)
                )
                st.plotly_chart(fig_metric, use_container_width=True, key=f"metric_{i}")
                st.markdown(f"<p style='text-align: center; font-size: 9px; margin-top: -10px;'>{label}</p>", unsafe_allow_html=True)

def main():
    """Main function to control navigation"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'menu'
            st.rerun()
        
        if st.button("📤 Update Data", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()
        
        if st.button("📊 View Dashboard", use_container_width=True):
            if st.session_state.df_ytd is not None and st.session_state.df_summary_present is not None:
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                st.warning("Please upload data first!")
        
        st.divider()
        
        # Data status
        st.subheader("Data Status")
        if st.session_state.df_ytd is not None and st.session_state.df_summary is not None:
            st.success("✅ Data loaded")
        else:
            st.warning("⚠️ No data loaded")
    
    # Main content area
    if st.session_state.page == 'menu':
        st.title("🏠 Risk Management System")
        st.write("Welcome to the Risk Management Dashboard")
        st.write("")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Update Data", use_container_width=True, key="menu_upload"):
                st.session_state.page = 'upload'
                st.rerun()
        
        with col2:
            if st.button("📊 View Dashboard", use_container_width=True, key="menu_dashboard"):
                if st.session_state.df_ytd is not None and st.session_state.df_summary_present is not None:
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.warning("Please upload data first!")
    
    elif st.session_state.page == 'upload':
        show_data_upload()
    
    elif st.session_state.page == 'dashboard':
        show_dashboard()

if __name__ == "__main__":
    main()