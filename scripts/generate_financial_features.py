import pandas as pd
import re
import glob
import os
import math

nrb_files = sorted(glob.glob('/home/saurav/Documents/Research/apex_journal/nrb_reports/Macroeconomic-Indicators-of-Nepal-*.xlsx'))

master_data = {}

def clean_year_table3(yr_str):
    if pd.isna(yr_str): return None
    yr_str = str(yr_str).strip()
    # e.g., '2023/24R' -> match '24' -> 2024
    # '2012/13' -> 2013
    m = re.search(r'/(\d{2})[A-Za-z]*', yr_str)
    if m:
        return 2000 + int(m.group(1))
    return None

def clean_year_table19(yr_val):
    if pd.isna(yr_val): return None
    try:
        y = int(float(str(yr_val).strip().replace('*', '')))
        if 2000 <= y <= 2100:
            return y
    except:
        pass
    return None

for file_path in nrb_files:
    print(f"Processing {os.path.basename(file_path)}")
    
    try:
        # ---- TABLE 3 ----
        df3 = pd.read_excel(file_path, sheet_name='3')
        
        # Find year row for Table 3
        year_row_idx = None
        for i in range(10):
            row_vals = df3.iloc[i].astype(str).tolist()
            if any('2012/13' in str(v) or '2013/14' in str(v) or '2019/20' in str(v) for v in row_vals):
                year_row_idx = i
                break
                
        if year_row_idx is not None:
            years3 = [clean_year_table3(v) for v in df3.iloc[year_row_idx].tolist()]
            
            # Find target rows
            gdp_row, cpi_row = None, None
            for i in range(len(df3)):
                val = str(df3.iloc[i, 0]).strip()
                if val == "Real GDP at Purchasers' Price":
                    gdp_row = df3.iloc[i].tolist()
                elif val == "National Consumer Price Index":
                    cpi_row = df3.iloc[i].tolist()
            
            for y, gdp, cpi in zip(years3, gdp_row or [], cpi_row or []):
                if y is not None:
                    if y not in master_data: master_data[y] = {}
                    if pd.notna(gdp) and isinstance(gdp, (int, float)):
                        master_data[y]['GDP_Growth'] = float(gdp)
                    if pd.notna(cpi) and isinstance(cpi, (int, float)):
                        master_data[y]['Inflation'] = float(cpi)
    except Exception as e:
        print(f"Error processing Table 3 in {file_path}: {e}")

    try:
        # ---- TABLE 19 ----
        df19 = pd.read_excel(file_path, sheet_name='19')
        
        # Find year row for Table 19
        year_row_idx = None
        for i in range(10):
            row_vals = df19.iloc[i].tolist()
            if any('2017' in str(v) or '2018' in str(v) for v in row_vals):
                year_row_idx = i
                break
                
        if year_row_idx is not None:
            years19 = [clean_year_table19(v) for v in df19.iloc[year_row_idx].tolist()]
            
            # Find target row
            ir_row = None
            for i in range(len(df19)):
                val = str(df19.iloc[i, 0]).strip()
                if "H. Weighted Average Lending Rate (Commercial Banks)" in val or "Weighted Average Lending Rate" in val:
                    ir_row = df19.iloc[i].tolist()
                    break
            
            if ir_row is not None:
                for y, ir in zip(years19, ir_row):
                    if y is not None:
                        if y not in master_data: master_data[y] = {}
                        if pd.notna(ir) and isinstance(ir, (int, float)):
                            master_data[y]['Interest_Rate'] = float(ir)
    except Exception as e:
        import traceback
        print(f"Error processing Table 19 in {file_path}:")
        traceback.print_exc()

# Build DataFrame
records = []
for y in sorted(master_data.keys()):
    rec = {'Year': y}
    rec.update(master_data[y])
    records.append(rec)

df_out = pd.DataFrame(records)

os.makedirs('/home/saurav/Documents/Research/apex_journal/data', exist_ok=True)
out_path = '/home/saurav/Documents/Research/apex_journal/data/macroecomics_features.csv'
df_out.to_csv(out_path, index=False)
print(f"Successfully generated features at {out_path}")
print(df_out.to_string())
