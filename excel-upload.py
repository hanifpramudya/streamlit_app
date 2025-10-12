import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Excel Data Viewer", page_icon="📊", layout="wide")

# Title
st.title("📊 Excel File Upload and Display")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Read the Excel file to get sheet names
        excel_file = pd.ExcelFile(uploaded_file)
        
        st.success(f"✅ File uploaded successfully!")
        st.write(f"**Available sheets:** {', '.join(excel_file.sheet_names)}")
        
        # Check if required sheets exist
        required_sheets = ["Data_YTD", "Summary"]
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
        
        if missing_sheets:
            st.warning(f"⚠️ Missing sheets: {', '.join(missing_sheets)}")
        
        # Display Data_YTD sheet
        if "Data_YTD" in excel_file.sheet_names:
            st.header("📈 Data_YTD Sheet")
            df_ytd = pd.read_excel(uploaded_file, sheet_name="Data_YTD")
            
            # Clean up Data_YTD sheet
            # Drop Unnamed: 0 and rename Unnamed: 1 to Parameter
            if 'Unnamed: 0' in df_ytd.columns:
                df_ytd = df_ytd.drop('Unnamed: 0', axis=1)
            if 'Unnamed: 1' in df_ytd.columns:
                df_ytd = df_ytd.rename(columns={'Unnamed: 1': 'Parameter'})
            
            # Replace "Unnamed: " columns with the value from the left column
            cols = list(df_ytd.columns)
            new_cols = []
            last_named = None
            
            for col in cols:
                col_str = str(col)
                if col_str.startswith('Unnamed: '):
                    new_cols.append(last_named if last_named else col)
                else:
                    new_cols.append(col)
                    if col != 'Parameter':  # Don't use Parameter as last_named
                        last_named = col
            
            df_ytd.columns = new_cols
            
            # Fill NaN in row 0 with values from the left (forward fill)
            if len(df_ytd) > 0:
                df_ytd.iloc[0] = df_ytd.iloc[0].fillna(method='ffill')
            
            # Create new header with format "row_0_value - original_column_name"
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
            
            st.write(f"**Total rows:** {len(df_ytd)}")
            st.write(f"**Total columns:** {len(df_ytd.columns)}")
            
            # Row selection slider for Data_YTD
            max_rows_ytd = len(df_ytd)
            if max_rows_ytd > 10:
                start_row_ytd = st.slider(
                    "Select starting row for Data_YTD", 
                    min_value=0, 
                    max_value=max_rows_ytd-10,
                    value=0,
                    key="ytd_slider"
                )
                st.subheader(f"Rows {start_row_ytd+1} to {start_row_ytd+10}")
                st.dataframe(df_ytd.iloc[start_row_ytd:start_row_ytd+10], use_container_width=True)
            else:
                st.subheader("All Rows")
                st.dataframe(df_ytd, use_container_width=True)
            
            with st.expander("📋 View All Data - Data_YTD"):
                st.dataframe(df_ytd, use_container_width=True, height=400)
            
            with st.expander("📋 Column Information - Data_YTD"):
                col_info_ytd = pd.DataFrame({
                    'Column Name': df_ytd.columns,
                    'Data Type': df_ytd.dtypes.values,
                    'Non-Null Count': df_ytd.count().values
                })
                st.dataframe(col_info_ytd, use_container_width=True)
            
            st.divider()
        
        # Display Summary sheet
        if "Summary" in excel_file.sheet_names:
            st.header("📊 Summary Sheet")
            df_summary = pd.read_excel(uploaded_file, sheet_name="Summary")
            
            # Clean up Summary sheet
            # Step 1: Move column names to row 0
            original_columns = df_summary.columns.tolist()
            df_summary.loc[-1] = original_columns  # Insert at index -1
            df_summary.index = df_summary.index + 1  # Shift index
            df_summary = df_summary.sort_index()  # Sort by index
            
            # Step 2: Create new temporary column names
            df_summary.columns = [f'Col_{i}' for i in range(len(df_summary.columns))]
            
            # Step 3: Drop first column (was Unnamed: 0)
            df_summary = df_summary.drop('Col_0', axis=1)
            
            # Step 4: Rename second column to Parameter
            df_summary = df_summary.rename(columns={'Col_1': 'Parameter'})
            
            # Step 5: Drop row 0 (original column names)
            df_summary = df_summary.iloc[1:].reset_index(drop=True)
            
            # Step 6: Fill NaN in current row 0 with values from the left (forward fill)
            if len(df_summary) > 0:
                df_summary.iloc[0] = df_summary.iloc[0].fillna(method='ffill')
            
            # Step 7: Fill NaN in current row 1 with values from the left (forward fill)
            if len(df_summary) > 1:
                df_summary.iloc[1] = df_summary.iloc[1].fillna(method='ffill')
            
            st.write(f"**Total rows:** {len(df_summary)}")
            st.write(f"**Total columns:** {len(df_summary.columns)}")
            
            # Row selection slider for Summary
            max_rows_summary = len(df_summary)
            if max_rows_summary > 10:
                start_row_summary = st.slider(
                    "Select starting row for Summary", 
                    min_value=0, 
                    max_value=max_rows_summary-10,
                    value=0,
                    key="summary_slider"
                )
                st.subheader(f"Rows {start_row_summary+1} to {start_row_summary+10}")
                st.dataframe(df_summary.iloc[start_row_summary:start_row_summary+10], use_container_width=True)
            else:
                st.subheader("All Rows")
                st.dataframe(df_summary, use_container_width=True)
            
            with st.expander("📋 View All Data - Summary"):
                st.dataframe(df_summary, use_container_width=True, height=400)
            
            with st.expander("📋 Column Information - Summary"):
                col_info_summary = pd.DataFrame({
                    'Column Name': df_summary.columns,
                    'Data Type': df_summary.dtypes.values,
                    'Non-Null Count': df_summary.count().values
                })
                st.dataframe(col_info_summary, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
else:
    st.info("👆 Please upload an Excel file to get started")
    st.write("**Note:** The file should contain sheets named 'Data_YTD' and 'Summary'")