import streamlit as st
from preprocess_data import process_excel_data

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
