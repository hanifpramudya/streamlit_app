import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Excel Data Viewer", page_icon="📊")

# Title
st.title("📊 Excel File Upload and Display")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)
        
        # Display file information
        st.success(f"✅ File uploaded successfully!")
        st.write(f"**Total rows:** {len(df)}")
        st.write(f"**Total columns:** {len(df.columns)}")
        
        # Display first 10 rows
        st.subheader("First 10 Rows of Data")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Optional: Display column names and data types
        with st.expander("📋 Column Information"):
            col_info = pd.DataFrame({
                'Column Name': df.columns,
                'Data Type': df.dtypes.values,
                'Non-Null Count': df.count().values
            })
            st.dataframe(col_info, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
else:
    st.info("👆 Please upload an Excel file to get started")
