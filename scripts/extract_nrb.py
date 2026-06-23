import pandas as pd
import numpy as np

excel_file = "/home/saurav/Documents/Research/apex_journal/nrb_reports/Macroeconomic-Indicators-of-Nepal-2025-December.xlsx"
xl = pd.ExcelFile(excel_file)

def get_row_data(sheet_name, row_keyword, data_start_col=1, header_row_idx=None):
    df = pd.read_excel(xl, sheet_name=sheet_name)
    
    # Find header row if not provided
    if header_row_idx is None:
        for i in range(10):
            row_vals = df.iloc[i].values
            if any("201" in str(v) or "202" in str(v) for v in row_vals):
                header_row_idx = i
                break
                
    if header_row_idx is None:
        return {}
        
    headers = df.iloc[header_row_idx].values
    
    # Extract years from headers
    years = []
    col_mapping = {}
    for col_idx in range(data_start_col, len(headers)):
        h = str(headers[col_idx]).strip()
        import re
        m = re.search(r"20\d{2}/(\d{2})", h)
        if m:
            year = 2000 + int(m.group(1))
            years.append(year)
            col_mapping[year] = col_idx
            
    # Find data row
    target_row = None
    for i in range(len(df)):
        row_vals = df.iloc[i].values
        if any(row_keyword.lower() in str(v).lower() for v in row_vals):
            target_row = i
            break
            
    if target_row is None:
        return {}
        
    data = {}
    for yr, col_idx in col_mapping.items():
        val = df.iloc[target_row, col_idx]
        try:
            data[yr] = float(val)
        except:
            data[yr] = np.nan
            
    return data

# Broad Money (M2) from Sheet 10
m2_data = get_row_data("10", "3. Broad Money (M2)")

# Workers Remittances from Sheet 25A / 25B
rem_data = get_row_data("25A", "Workers' Remittances")
rem_data_b = get_row_data("25B", "O/W Workers' remittances")
rem_data.update(rem_data_b)

# Gross Foreign Exchange from Sheet 26
forex_data = get_row_data("26", "1.Gross Foreign Exchange Reserve")

print("M2:", m2_data)
print("Remittances:", rem_data)
print("Forex:", forex_data)

# Load macro CSV and merge
file_path = "/home/saurav/Documents/Research/apex_journal/data/macroecomics_features.csv"
df_macro = pd.read_csv(file_path)

if "Broad_Money_M2_Rs_Cr" not in df_macro.columns:
    df_macro["Broad_Money_M2_Rs_Cr"] = np.nan
    df_macro["Workers_Remittances_Rs_Cr"] = np.nan
    df_macro["Gross_Forex_Reserves_Rs_Cr"] = np.nan

for i, row in df_macro.iterrows():
    yr = row["Year"]
    if yr in m2_data: df_macro.at[i, "Broad_Money_M2_Rs_Cr"] = m2_data[yr] / 10 # Convert millions to crores
    if yr in rem_data: df_macro.at[i, "Workers_Remittances_Rs_Cr"] = rem_data[yr] / 10
    if yr in forex_data: df_macro.at[i, "Gross_Forex_Reserves_Rs_Cr"] = forex_data[yr] / 10

df_macro.to_csv(file_path, index=False)
print(df_macro.to_string())
