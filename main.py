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
    st.title("Risk Management Dashboard")

    # Legend in horizontal layout
    with st.container(border=True):
        st.markdown("#### Legend")
        st.markdown('''
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <span><span style="color: #90d050; font-size: 20px;">●</span> Low</span>
                <span><span style="color: #fff2cc; font-size: 20px;">●</span> Low to Moderate</span>
                <span><span style="color: #ffff00; font-size: 20px;">●</span> Moderate</span>
                <span><span style="color: #ffc001; font-size: 20px;">●</span> Moderate to High</span>
                <span><span style="color: #ff0000; font-size: 20px;">●</span> High</span>
            </div>
        ''', unsafe_allow_html=True)

    # Date selector
    date_col1, date_col2 = st.columns([1, 5])
    with date_col1:
        if latest_col_ytd_idx and st.session_state.df_ytd is not None:
            # Get columns up to latest_col_ytd_idx, excluding 'Parameter'
            col_position = st.session_state.df_ytd.columns.get_loc(latest_col_ytd_idx)
            available_dates = [col for col in st.session_state.df_ytd.columns[:col_position+1] if col != 'Parameter']
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

    col_summary, col_nps= st.columns([3, 2])
    
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
        # Safely get the composite score
        try:
            composite_score = float(st.session_state.df_summary_present['present_month'].iloc[10])
        except:
            composite_score = 0.0
        
        st.markdown(f"<p style='text-align: center;'><strong>Average Risk</strong><br>Composite Score in {available_dates[-1]} is {composite_score:.2f}</p>", unsafe_allow_html=True)
        
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
    
    # Dropdown for risk type
    risk_types = ["Keseluruhan Risiko"]
    if 'Jenis Risiko' in st.session_state.df_summary.columns:
        risk_types.extend(st.session_state.df_summary['Jenis Risiko'][:9].tolist())
    
    st.selectbox("Select Risk Type", risk_types, label_visibility="collapsed")
    
    # Financial Metrics Section
    titles = ["Jumlah Aset", "Jumlah Utang", "Jumlah Ekuitas", "Jumlah Polis", "Kas dan Bank", "Aset Investasi", "RBC"]

    # Create 7 columns: 6 equal-sized, 1 larger for RBC
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1.5])
    cols = [col1, col2, col3, col4, col5, col6, col7]
    value_idx = [9,14,15,116,5,0,51]

    # Display all 7 containers
    for i, col in enumerate(cols):
        with col:
            with st.container(border=True):
                # Display title
                st.markdown(f"<div style='text-align: center; color: #999; font-size: 12px;'>{titles[i]}</div>", unsafe_allow_html=True)
                # Get value from df_ytd
                if st.session_state.df_ytd is not None and latest_col_ytd_idx:
                    try:
                        value = st.session_state.df_ytd[latest_col_ytd_idx].iloc[value_idx[i]]
                        # RBC gets larger and red font
                        if i == 6:
                            st.markdown(f"<div style='text-align: center; font-size: 32px; font-weight: bold; color: #ff6347; margin: 5px 0;'>{value}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: center; font-size: 24px; font-weight: bold; color: #333; margin: 5px 0;'>{value}</div>", unsafe_allow_html=True)
                    except:
                        st.markdown("<div style='text-align: center; font-size: 24px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; font-size: 24px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)

    # Line Graphs and Pie Charts Section
    col_graphs, col_pies = st.columns(2)

    # First column - Line Graphs with Tabs
    with col_graphs:
        # Line graph titles
        line_titles = ["Jumlah Pendapatan", "Premi Bruto (All)", "Klaim Bruto (All)", "Agjal Laba (Rugi) Komprehensif"]

        # Create tabs
        tabs_line = st.tabs(["All Graphs", line_titles[0], line_titles[1], line_titles[2], line_titles[3]])

        # Get present_col_ytd (last 12 months from latest_col_ytd_idx)
        if st.session_state.df_ytd is not None and latest_col_ytd_idx:
            try:
                col_position = st.session_state.df_ytd.columns.get_loc(latest_col_ytd_idx)
                present_col_ytd = st.session_state.df_ytd.columns[max(0, col_position - 11):col_position + 1]

                # Tab 0: All Graphs
                value_idx = [3, 16, 26, 43]
                with tabs_line[0]:
                    for idx, title in enumerate(line_titles):
                        try:
                            # Get data for this metric across present_col_ytd
                            dates = [col for col in present_col_ytd]
                            values = [st.session_state.df_ytd[col].iloc[value_idx[idx]] for col in present_col_ytd]

                            # Create line chart
                            fig_line = go.Figure()
                            fig_line.add_trace(go.Scatter(
                                x=dates,
                                y=values,
                                mode='lines+markers',
                                name=title,
                                line=dict(width=2),
                                marker=dict(size=6)
                            ))
                            fig_line.update_layout(
                                title=title,
                                height=200,
                                margin=dict(l=40, r=20, t=40, b=30),
                                xaxis=dict(showgrid=True),
                                yaxis=dict(showgrid=True),
                                plot_bgcolor='white'
                            )
                            st.plotly_chart(fig_line, use_container_width=True, key=f"line_all_{idx}")
                        except:
                            st.warning(f"Unable to load data for {title}")

                # Tabs 1-4: Individual Graphs
                value_idx = [25, 16, 26, 43]
                for tab_idx in range(1, 5):
                    with tabs_line[tab_idx]:
                        try:
                            title = line_titles[tab_idx - 1]
                            dates = [col for col in present_col_ytd]
                            values = [st.session_state.df_ytd[col].iloc[value_idx[tab_idx - 1]] for col in present_col_ytd]

                            fig_line = go.Figure()
                            fig_line.add_trace(go.Scatter(
                                x=dates,
                                y=values,
                                mode='lines+markers',
                                name=title,
                                line=dict(width=3),
                                marker=dict(size=8)
                            ))
                            fig_line.update_layout(
                                title=title,
                                height=450,
                                margin=dict(l=40, r=20, t=40, b=30),
                                xaxis=dict(showgrid=True),
                                yaxis=dict(showgrid=True),
                                plot_bgcolor='white'
                            )
                            st.plotly_chart(fig_line, use_container_width=True, key=f"line_single_{tab_idx}")
                        except:
                            st.warning(f"Unable to load data")
            except:
                st.warning("Unable to load line graph data")
        else:
            st.warning("No data available for line graphs")

    # Second column - Pie Charts with Tabs
    with col_pies:
        # Pie chart titles
        pie_titles = ["Deposito Berjangka", "Obligasi Korporasi", "Surat Berharga yang Diterbitkan oleh Negara RI", "Reksa Dana"]
        value_idx = [1,2,3,4]
        # Create tabs
        tabs_pie = st.tabs(["All Graphs", pie_titles[0], pie_titles[1], pie_titles[2], pie_titles[3]])

        if st.session_state.df_ytd is not None and latest_col_ytd_idx:
            try:
                col_position = st.session_state.df_ytd.columns.get_loc(latest_col_ytd_idx)
                present_col_ytd = st.session_state.df_ytd.columns[max(0, col_position - 11):col_position + 1]

                # Tab 0: All Graphs - Single Pie Chart with All Categories
                with tabs_pie[0]:
                    try:
                        # Get values for all four categories
                        labels = []
                        values_pie = []

                        for idx, title in enumerate(pie_titles):
                            value = st.session_state.df_ytd[latest_col_ytd_idx].iloc[value_idx[idx]]
                            value_float = float(value) if pd.notna(value) else 0
                            labels.append(title)
                            values_pie.append(value_float)

                        # Create pie chart with all four categories
                        fig_pie = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values_pie,
                            hole=0.3,
                            textinfo='label+percent',
                            textposition='auto'
                        )])
                        fig_pie.update_layout(
                            title="Distribusi Portfolio Investasi",
                            height=400,
                            margin=dict(l=10, r=10, t=40, b=80),
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.3,
                                xanchor="center",
                                x=0.5
                            )
                        )
                        st.plotly_chart(fig_pie, use_container_width=True, key="pie_all_combined")
                    except Exception as e:
                        st.warning(f"Unable to load pie chart data: {str(e)}")

                # Tabs 1-4: Individual Pie Charts - Full portion of each investment type
                for tab_idx in range(1, 5):
                    with tabs_pie[tab_idx]:
                        try:
                            title = pie_titles[tab_idx - 1]
                            value = st.session_state.df_ytd[latest_col_ytd_idx].iloc[value_idx[tab_idx - 1]]
                            value_float = float(value) if pd.notna(value) else 0

                            # Create full pie chart showing 100% of this investment type
                            labels = [title]
                            values_pie = [100]  # Full 100% pie

                            fig_pie = go.Figure(data=[go.Pie(
                                labels=labels,
                                values=values_pie,
                                hole=0.3,
                                textinfo='label+value',
                                textposition='inside',
                                text=[f"{value_float}"]
                            )])
                            fig_pie.update_layout(
                                title=f"{title}: {value_float}",
                                height=450,
                                margin=dict(l=20, r=20, t=40, b=20),
                                showlegend=False
                            )
                            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_single_{tab_idx}")
                        except Exception as e:
                            st.warning(f"Unable to load data: {str(e)}")
            except:
                st.warning("Unable to load pie chart data")
        else:
            st.warning("No data available for pie charts")

    # Additional Metrics Section - 3 columns with multiple rows
    col_a, col_b, col_c = st.columns(3)
    value_idx = [139,141,143]

    # First column - 3 rows
    with col_a:
        titles_col_a = ["Jumlah Pengaduan", "Indak Lanjut Pengaduan", "Jumlah Pemberitaan Negatif Dalam 1 Tahun"]
        for i, title in enumerate(titles_col_a):
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; color: #999; font-size: 12px;'>{title}</div>", unsafe_allow_html=True)
                if st.session_state.df_ytd is not None and latest_col_ytd_idx:
                    try:
                        # Offset index by 7 since previous section used 0-6
                        value = st.session_state.df_ytd[latest_col_ytd_idx].iloc[value_idx[i]]
                        st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>{value}</div>", unsafe_allow_html=True)
                    except:
                        st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)

    # Second column - 2 rows
    with col_b:
        titles_col_b = ["Jumlah Fraud","Jumlah Gugatan", "Jumlah Nominal Gugatan Yang Sedang Diajukan"]
        value_idx = [117,132,133]
        for i, title in enumerate(titles_col_b):
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; color: #999; font-size: 12px;'>{title}</div>", unsafe_allow_html=True)
                if st.session_state.df_ytd is not None and latest_col_ytd_idx:
                    try:
                        # Offset index by 10 (7 from first section + 3 from col_a)
                        value = st.session_state.df_ytd[latest_col_ytd_idx].iloc[value_idx[i]]
                        st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>{value}</div>", unsafe_allow_html=True)
                    except:
                        st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)

    # Third column - 2 rows
    with col_c:
        titles_col_c = ["Jumlah Pelanggaran Atas Ketentuan", "Jumlah Denda"]
        value_idx = [134,137]
        for i, title in enumerate(titles_col_c):
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; color: #999; font-size: 12px;'>{title}</div>", unsafe_allow_html=True)
                if st.session_state.df_ytd is not None and latest_col_ytd_idx:
                    try:
                        # Offset index by 12 (7 + 3 + 2)
                        value = st.session_state.df_ytd[latest_col_ytd_idx].iloc[value_idx[i]]
                        st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>{value}</div>", unsafe_allow_html=True)
                    except:
                        st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: #333; margin: 5px 0;'>-</div>", unsafe_allow_html=True)
                    
def main():
    """Main function to control navigation"""
    
    # Sidebar navigation
    with st.sidebar:
        st.image("Logo.png")

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
