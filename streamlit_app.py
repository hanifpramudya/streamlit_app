import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
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
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.title("Risk Management Dashboard")
with col2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Astra_logo.svg/320px-Astra_logo.svg.png", width=120)

# Date selector
date_col1, date_col2 = st.columns([1, 5])
with date_col1:
    selected_date = st.selectbox("", ["Maret 2025"], label_visibility="collapsed")

# Summary Section
st.markdown("### Summary")

# Create summary table with NPS Score
col_summary, col_nps, col_legend = st.columns([2, 1.5, 1])

with col_summary:
    # Create risk matrix data
    risk_data = {
        'Category': ['Operasional', 'Kepatuhan', 'Reputasi'],
        'Prev Month': [2.3, 2.3, 2.3],
        'Present Month': [2.3, 2.3, 3.0]
    }
    
    # Display as colored table
    st.markdown('<div class="risk-table">', unsafe_allow_html=True)
    
    df = pd.DataFrame(risk_data)
    
    # Create custom styled table
    def color_cells(val):
        if val == 2.3:
            return 'background-color: #90EE90'
        elif val == 3.0:
            return 'background-color: #FFD700'
        else:
            return ''
    
    styled_df = df.style.applymap(color_cells, subset=['Prev Month', 'Present Month'])
    st.dataframe(styled_df, hide_index=True, use_container_width=True, height=150)
    st.markdown('</div>', unsafe_allow_html=True)

with col_nps:
    st.markdown("#### 💎 NPS Score")
    st.markdown("**Average Risk** - NPS Score is +78")
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=78,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "black"},
            'bgcolor': "white",
            'borderwidth': 2,
            'steps': [
                {'range': [0, 20], 'color': '#90EE90'},
                {'range': [20, 40], 'color': '#98D98E'},
                {'range': [40, 60], 'color': '#FFD700'},
                {'range': [60, 80], 'color': '#FFA500'},
                {'range': [80, 100], 'color': '#DC143C'}
            ],
        }
    ))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="nps_gauge")

with col_legend:
    st.markdown("")
    st.markdown("")
    st.markdown("🟢 Low")
    st.markdown("🟢 Low to Moderate")
    st.markdown("🟡 Moderate")
    st.markdown("🟠 Moderate to High")
    st.markdown("🔴 High")

# Dropdown for risk type
st.selectbox("Keseluruhan Risiko", ["Keseluruhan Risiko"], label_visibility="collapsed")

# Survey and GRC Section - Single row with all cards
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
    
    # CSAT Trend Chart
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
    
    # CSAT Score with gauge and metrics
    st.markdown("**CSAT Score**")
    
    # Main gauge
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
    
    # Metrics in circles - 2 rows of 3
    metrics_data = [
        ("Technical Copebilitis", "46%"),
        ("Timely Deliverie", "74%"),
        ("Quality of Deliverable", "14%"),
        ("Program Governance", "46%"),
        ("New Ideas & Creative Solution", "54%"),
        ("New Ideas & Creative Solution", "54%")
    ]
    
    # First row
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
    
    # Second row
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
