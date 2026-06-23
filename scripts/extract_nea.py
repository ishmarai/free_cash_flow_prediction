import PyPDF2
import glob
import re
import pandas as pd
import os

pdf_files = sorted(glob.glob("/home/saurav/Documents/Research/apex_journal/nea_annual_reports/*.pdf"))

data = []

for pdf_path in pdf_files:
    year_match = re.search(r"(\d{4})-\d{4}", pdf_path)
    if not year_match:
        continue
    start_year = int(year_match.group(1))
    target_year = start_year + 1 # e.g. 2024-2025 -> 2025
    
    print(f"Processing {target_year}...")
    try:
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t: text += t + "\n"
                
        # Clean text
        text_clean = re.sub(r'\s+', ' ', text)
        
        # 1. Total IPP Generation (MU or GWh)
        # Look for things like "Purchase from IPP", "IPP Purchase", "from IPPs" followed by numbers
        ipp_gen = None
        # Try to find a standalone table row like: Power Purchase from IPPs 1,012 1,623
        ipp_matches = re.findall(r"Purchase from IPPs?\s+([\d,.]+)", text_clean, re.IGNORECASE)
        if ipp_matches:
            try:
                # take the last one or the most reasonable looking one
                vals = [float(m.replace(',', '')) for m in ipp_matches if m.replace(',', '').replace('.','').isdigit()]
                if vals:
                    ipp_gen = max(vals) # rough heuristic
            except:
                pass
                
        if ipp_gen is None:
            # Another pattern: "IPPs supplied XX%" or "purchased XX GWh from IPP"
            m2 = re.search(r"purchased\s+([\d,.]+)\s*(GWh|MU)\s*from IPP", text_clean, re.IGNORECASE)
            if m2:
                ipp_gen = float(m2.group(1).replace(',', ''))
                
        # 2. Average Bulk Purchase Tariff
        # Look for "Average Bulk Purchase Tariff", "Average purchase rate from IPP", etc.
        tariff = None
        t_matches = re.findall(r"Average\s+(?:Bulk\s+)?Purchase\s+(?:Tariff|Rate)[^\d]{0,30}([\d.]+)", text_clean, re.IGNORECASE)
        if t_matches:
            try:
                vals = [float(m) for m in t_matches if 1.0 < float(m) < 20.0] # Realistic Rs/kWh limits
                if vals:
                    tariff = sum(vals)/len(vals) # Average of mentions
            except:
                pass
                
        data.append({
            "Year": target_year,
            "Total_IPP_Generation_GWh": ipp_gen,
            "Average_Bulk_Purchase_Tariff_Rs": tariff
        })
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

df = pd.DataFrame(data)

# Hardcode the known highly accurate IPP generation table from 2024-2025 report (Page 137)
# 2016: 1012, 2017: 1623, 2018: 2019, 2019: 2033, 2020: 2836, 2021: 3093, 2022: 4286, 2023: 5118, 2024: 6564, 2025: 8606
known_ipp = {
    2016: 1012, 2017: 1623, 2018: 2019, 2019: 2033, 2020: 2836, 
    2021: 3093, 2022: 4286, 2023: 5118, 2024: 6564, 2025: 8606
}

for yr, val in known_ipp.items():
    idx = df[df["Year"] == yr].index
    if not idx.empty:
        df.loc[idx, "Total_IPP_Generation_GWh"] = val

out_path = "/home/saurav/Documents/Research/apex_journal/data/nea_macro_features.csv"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
df.to_csv(out_path, index=False)
print(f"Successfully generated {out_path}")
print(df.to_string())
