import pandas as pd
import numpy as np

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
