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
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-table {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .summary-box {
        background-color: #e8e8e8;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .survey-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .grc-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .grc-number {
        font-size: 48px;
        color: #ff6347;
        font-weight: bold;
    }
    .survey-number {
        font-size: 36px;
        font-weight: bold;
        color: #333;
    }
    .survey-label {
        color: #999;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Risk Management Dashboard")
with col2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Astra_logo.svg/320px-Astra_logo.svg.png", width=150)

# Date selector
date_col = st.columns([1, 4])
with date_col[0]:
    selected_date = st.selectbox("", ["Maret 2025"], label_visibility="collapsed")

# Summary Section
st.markdown("### Summary")

# Create summary table with NPS Score
col_summary, col_nps = st.columns([2, 1])

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
    st.dataframe(styled_df, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_nps:
    st.markdown("#### 💎 NPS Score")
    st.markdown("**Average Risk**")
    st.markdown("NPS Score is +78")
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=78,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Tolerance", 'font': {'size': 12}},
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
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk legend
    st.markdown("🟢 Low")
    st.markdown("🟢 Low to Moderate")
    st.markdown("🟡 Moderate")
    st.markdown("🟠 Moderate to High")
    st.markdown("🔴 High")

# Dropdown for risk type
st.selectbox("Keseluruhan Risiko", ["Keseluruhan Risiko"])

# Survey and GRC Section
col1, col2, col3, col4, col5, col6 = st.columns(6)

survey_cols = [col1, col2, col3, col4]
for col in survey_cols:
    with col:
        st.markdown('<div class="survey-card">', unsafe_allow_html=True)
        st.markdown('<div class="survey-label">Survey</div>', unsafe_allow_html=True)
        st.markdown('<div class="survey-number">60</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Second row of surveys
col1, col2, col3, col4, col5, col6 = st.columns(6)

survey_cols2 = [col1, col2, col3, col4]
for col in survey_cols2:
    with col:
        st.markdown('<div class="survey-card">', unsafe_allow_html=True)
        st.markdown('<div class="survey-label">Survey</div>', unsafe_allow_html=True)
        st.markdown('<div class="survey-number">60</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

grc_cols = [col5, col6]
for col in grc_cols:
    with col:
        st.markdown('<div class="grc-card">', unsafe_allow_html=True)
        st.markdown('<div class="survey-label">GRC</div>', unsafe_allow_html=True)
        st.markdown('<div class="grc-number">06</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bottom Section
col_left, col_middle, col_right = st.columns([1, 2, 2])

with col_left:
    st.markdown("#### Jumlah gugatan")
    st.text_area("", "", height=150, label_visibility="collapsed")
    
    st.markdown("#### Jumlah Fraud")
    st.text_area("", "", height=150, label_visibility="collapsed", key="fraud")

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
        marker=dict(size=10, color='#20B2AA')
    ))
    
    fig_trend.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(range=[0, 8.5], showgrid=True, gridcolor='lightgray'),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.button("Pilih Variabel", use_container_width=True, key="var2")
    
    # CSAT Score with gauge and metrics
    st.markdown("**CSAT Score**")
    
    # Main gauge
    fig_csat = go.Figure(go.Indicator(
        mode="gauge+number",
        value=8.44,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': '', 'font': {'size': 40}},
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
        height=200,
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[
            dict(text="▲ 25.09%", x=0.5, y=0.3, showarrow=False, font=dict(size=12)),
            dict(text="Current Year - Last Year", x=0.5, y=0.15, showarrow=False, font=dict(size=10, color='gray'))
        ]
    )
    st.plotly_chart(fig_csat, use_container_width=True)
    
    # Metrics in circles
    metrics_cols = st.columns(3)
    
    metrics_data = [
        ("Technical Copebilitis", "46%"),
        ("Timely Deliverie", "74%"),
        ("Quality of Deliverable", "14%"),
        ("Program Governance", "46%"),
        ("New Ideas & Creative Solution", "54%"),
        ("New Ideas & Creative Solution", "54%")
    ]
    
    for i, (label, value) in enumerate(metrics_data):
        col_idx = i % 3
        with metrics_cols[col_idx]:
            fig_metric = go.Figure(go.Indicator(
                mode="gauge+number",
                value=int(value.strip('%')),
                domain={'x': [0, 1], 'y': [0, 1]},
                number={'suffix': '%', 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [0, 100], 'visible': False},
                    'bar': {'color': "white", 'thickness': 0},
                    'bgcolor': "white",
                    'borderwidth': 3,
                    'bordercolor': '#20B2AA',
                    'steps': [
                        {'range': [0, int(value.strip('%'))], 'color': '#20B2AA'},
                        {'range': [int(value.strip('%')), 100], 'color': '#E0E0E0'}
                    ],
                }
            ))
            fig_metric.update_layout(
                height=120,
                margin=dict(l=10, r=10, t=0, b=0)
            )
            st.plotly_chart(fig_metric, use_container_width=True, key=f"metric_{i}")
            st.markdown(f"<p style='text-align: center; font-size: 10px;'>{label}</p>", unsafe_allow_html=True)
