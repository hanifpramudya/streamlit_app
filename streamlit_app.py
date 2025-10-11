import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Excel Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("📊 Interactive Excel Dashboard")
st.markdown("---")

# Sidebar for file upload and filters
with st.sidebar:
    st.header("📁 Data Source")
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

    st.markdown("---")
    st.header("⚙️ Settings")

    if uploaded_file:
        st.success("✅ File loaded successfully!")

# Main content
if uploaded_file is None:
    st.info("👈 Please upload an Excel file to begin")
    st.markdown("### Sample Data Format")
    st.markdown("Your Excel file should contain columns like:")
    st.code("""
    Date | Product | Category | Sales | Quantity | Region
    """)
else:
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)

        # Display sheet selector if multiple sheets
        excel_file = pd.ExcelFile(uploaded_file)
        if len(excel_file.sheet_names) > 1:
            with st.sidebar:
                selected_sheet = st.selectbox("Select Sheet", excel_file.sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        # Data preview section
        with st.expander("🔍 View Raw Data"):
            st.dataframe(df, use_container_width=True)
            st.download_button(
                label="📥 Download Filtered Data",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='filtered_data.csv',
                mime='text/csv'
            )

        # Filters in sidebar
        with st.sidebar:
            st.markdown("### 🔎 Filters")

            # Dynamic filters based on columns
            filters = {}
            for col in df.columns:
                if df[col].dtype == 'object' and df[col].nunique() < 50:
                    unique_vals = ['All'] + sorted(df[col].unique().tolist())
                    filters[col] = st.multiselect(
                        f"Filter by {col}",
                        options=unique_vals,
                        default=['All']
                    )

        # Apply filters
        filtered_df = df.copy()
        for col, selected_vals in filters.items():
            if 'All' not in selected_vals and selected_vals:
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

        # Key Metrics
        st.header("📈 Key Metrics")

        # Auto-detect numeric columns for metrics
        numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if numeric_cols:
            cols = st.columns(min(4, len(numeric_cols)))
            for idx, col_name in enumerate(numeric_cols[:4]):
                with cols[idx]:
                    total = filtered_df[col_name].sum()
                    avg = filtered_df[col_name].mean()
                    st.metric(
                        label=col_name.title(),
                        value=f"{total:,.0f}",
                        delta=f"Avg: {avg:,.1f}"
                    )

        st.markdown("---")

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Distribution Analysis")
            if numeric_cols:
                selected_metric = st.selectbox("Select Metric", numeric_cols, key='metric1')
                categorical_cols = filtered_df.select_dtypes(include=['object']).columns.tolist()

                if categorical_cols:
                    selected_category = st.selectbox("Group By", categorical_cols, key='cat1')

                    # Create bar chart
                    chart_data = filtered_df.groupby(selected_category)[selected_metric].sum().reset_index()
                    fig = px.bar(
                        chart_data,
                        x=selected_category,
                        y=selected_metric,
                        title=f"{selected_metric} by {selected_category}",
                        color=selected_metric,
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🥧 Composition Analysis")
            if numeric_cols:
                pie_metric = st.selectbox("Select Metric", numeric_cols, key='metric2')
                categorical_cols = filtered_df.select_dtypes(include=['object']).columns.tolist()

                if categorical_cols:
                    pie_category = st.selectbox("Group By", categorical_cols, key='cat2')

                    # Create pie chart
                    pie_data = filtered_df.groupby(pie_category)[pie_metric].sum().reset_index()
                    fig = px.pie(
                        pie_data,
                        values=pie_metric,
                        names=pie_category,
                        title=f"{pie_metric} Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Time series if date column exists
        date_cols = filtered_df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
        if date_cols and numeric_cols:
            st.markdown("---")
            st.subheader("📅 Time Series Analysis")

            date_col = st.selectbox("Select Date Column", date_cols)
            ts_metric = st.selectbox("Select Metric", numeric_cols, key='ts_metric')

            try:
                filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
                ts_data = filtered_df.groupby(date_col)[ts_metric].sum().reset_index()

                fig = px.line(
                    ts_data,
                    x=date_col,
                    y=ts_metric,
                    title=f"{ts_metric} Over Time",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Could not parse date column. Please ensure it's in a valid date format.")

        # Summary Statistics
        st.markdown("---")
        st.subheader("📋 Summary Statistics")
        st.dataframe(filtered_df.describe(), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("Please ensure your Excel file is properly formatted and not corrupted.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
