import pandas as pd
import numpy as np
import difflib
import re

def normalize_name(name):
    if pd.isna(name): return ""
    name = str(name).lower()
    # Remove common corporate suffixes and hydropower words to get the core name
    remove_words = [
        r'\bltd\.?\b', r'\blimited\b', r'\bco\.?\b', r'\bcompany\b', 
        r'\bhydro\b', r'\bhydropower\b', r'\bpower\b', r'\benergy\b',
        r'\bjalavidyut\b', r'\bjalabidyut\b', r'\bdevelopment\b', 
        r'\bproject\b', r'\bprivate\b', r'\bpvt\.?\b', r'[,.\(\)]'
    ]
    for w in remove_words:
        name = re.sub(w, '', name)
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def main():
    print("Loading datasets...")
    # Load Nepse Ticker Mapping
    df_listed = pd.read_csv("misc_data/listed_hydro.csv")
    df_listed.columns = df_listed.columns.str.strip()
    
    # Load DoED Data
    df_doed1 = pd.read_csv("misc_data/doed_hydro_greater_then_1MW.csv")
    df_doed2 = pd.read_csv("misc_data/doed_hydro_less_then_1MW.csv")
    df_doed3 = pd.read_csv("misc_data/doed_solar_license.csv")
    df_doed = pd.concat([df_doed1, df_doed2, df_doed3], ignore_index=True)
    
    # Create normalized columns for matching
    df_listed['NormName'] = df_listed['Name'].apply(normalize_name)
    df_doed['NormPromoter'] = df_doed['Promoter'].apply(normalize_name)
    df_doed['NormProject'] = df_doed['Project'].apply(normalize_name)
    
    print(f"Total Tickers: {len(df_listed)}")
    print(f"Total DoED Licenses: {len(df_doed)}")
    
    mapping_results = []
    
    doed_promoter_list = df_doed['NormPromoter'].dropna().unique().tolist()
    doed_project_list = df_doed['NormProject'].dropna().unique().tolist()
    
    for idx, row in df_listed.iterrows():
        ticker = row['Symbol']
        name = row['Name']
        norm_name = row['NormName']
        
        # 1. Try to match against Promoter
        matches = difflib.get_close_matches(norm_name, doed_promoter_list, n=1, cutoff=0.7)
        doed_row = None
        
        if matches:
            matched_norm = matches[0]
            doed_row = df_doed[df_doed['NormPromoter'] == matched_norm].iloc[0]
        else:
            # 2. Try to match against Project name
            matches = difflib.get_close_matches(norm_name, doed_project_list, n=1, cutoff=0.7)
            if matches:
                matched_norm = matches[0]
                doed_row = df_doed[df_doed['NormProject'] == matched_norm].iloc[0]
                
        if doed_row is not None:
            issue_date = str(doed_row.get('Isuue Date', ''))
            validity = str(doed_row.get('Validity', ''))
            
            # Extract years (Assuming Bikram Sambat YYYY-MM-DD)
            issue_yr = np.nan
            term = np.nan
            try:
                if len(issue_date) >= 4:
                    issue_yr = int(issue_date[:4])
                if len(validity) >= 4 and len(issue_date) >= 4:
                    term = int(validity[:4]) - int(issue_date[:4])
            except:
                pass
                
            mapping_results.append({
                'Ticker': ticker,
                'Company_Name': name,
                'Matched_Promoter': doed_row.get('Promoter', ''),
                'Matched_Project': doed_row.get('Project', ''),
                'Installed_Capacity_MW': doed_row.get('Capacity (MW)', np.nan),
                'License_Issue_Year': issue_yr,
                'License_Term_Years': term
            })
        else:
            # Failed to match
            mapping_results.append({
                'Ticker': ticker,
                'Company_Name': name,
                'Matched_Promoter': 'UNMATCHED',
                'Matched_Project': 'UNMATCHED',
                'Installed_Capacity_MW': np.nan,
                'License_Issue_Year': np.nan,
                'License_Term_Years': np.nan
            })
            
    df_map = pd.DataFrame(mapping_results)
    
    match_rate = len(df_map[df_map['Matched_Promoter'] != 'UNMATCHED']) / len(df_map) * 100
    print(f"Match Rate: {match_rate:.1f}%")
    
    # Save the mapping
    df_map.to_csv("data/operational_mapping.csv", index=False)
    print("Saved operational mapping to data/operational_mapping.csv")
    
    # Now merge into financial_statement_features.csv
    print("Updating financial_statement_features.csv...")
    features = pd.read_csv("data/financial_statement_features.csv")
    
    # Merge
    features = features.merge(
        df_map[['Ticker', 'Installed_Capacity_MW', 'License_Issue_Year', 'License_Term_Years']], 
        on='Ticker', 
        how='left'
    )
    
    # Calculate PLF and Tariffs
    features['PPA_Tariff_Wet'] = 4.80
    features['PPA_Tariff_Dry'] = 8.40
    blended_tariff = 6.00 # (4.80 * 8/12) + (8.40 * 4/12)
    
    # Revenue is in Rs '000. So Revenue * 1000 = Rs.
    # Capacity is in MW. Capacity * 1000 = kW.
    # Hours in year = 8760
    # PLF = Total Rs / (kW * 8760 * Rs/kWh)
    
    # Avoid division by zero
    cap_kw = features['Installed_Capacity_MW'] * 1000
    max_revenue_potential = cap_kw * 8760 * blended_tariff
    
    features['PLF'] = np.where(
        max_revenue_potential > 0,
        (features['Revenue'] * 1000) / max_revenue_potential,
        np.nan
    )
    
    # Clean up PLF (cap at 1.0, floor at 0.0)
    features['PLF'] = features['PLF'].clip(lower=0.0, upper=1.0)
    
    # Save back
    features.to_csv("data/financial_statement_features.csv", index=False)
    print("Done updating financial_statement_features.csv")
    
    print("\nSample of Unmatched Tickers:")
    print(df_map[df_map['Matched_Promoter'] == 'UNMATCHED'][['Ticker', 'Company_Name']].head(10))

if __name__ == "__main__":
    main()
