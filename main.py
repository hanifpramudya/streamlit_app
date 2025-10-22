import streamlit as st
from show_upload_data import show_data_upload
from dashboard import show_dashboard

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
