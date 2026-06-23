import pandas as pd

def main():
    print("Loading datasets...")
    
    # 1. Financial Features (Base)
    try:
        df_fin = pd.read_csv("data/financial_statement_features.csv")
    except FileNotFoundError:
        print("Error: financial_statement_features.csv not found.")
        return
        
    # 2. Operational Features
    try:
        df_op = pd.read_csv("data/operational_features.csv")
        # Drop redundant 'Year' column if 'Year_Int' is present to avoid suffixing during merge
        if 'Year' in df_op.columns and 'Year' in df_fin.columns:
            df_op = df_op.drop(columns=['Year'])
    except FileNotFoundError:
        print("Error: operational_features.csv not found.")
        return

    # 3. Macroeconomic Features (NRB)
    try:
        df_macro = pd.read_csv("data/macroecomics_features.csv")
    except FileNotFoundError:
        print("Error: macroecomics_features.csv not found.")
        return
        
    # 4. NEA Systemic Features
    try:
        df_nea = pd.read_csv("data/nea_macro_features_imputed.csv")
    except FileNotFoundError:
        print("Error: nea_macro_features_imputed.csv not found.")
        return

    print(f"Base financial records: {len(df_fin)}")

    # MERGE 1: Financial + Operational
    # Both have Ticker and Year_Int
    master_df = pd.merge(df_fin, df_op, on=['Ticker', 'Year_Int'], how='left')
    
    # MERGE 2: Master + Macro
    # Macro has 'Year' which maps to 'Year_Int'
    # Drop Year from macro after merge to avoid duplicates
    master_df = pd.merge(master_df, df_macro, left_on='Year_Int', right_on='Year', how='left', suffixes=('', '_macro'))
    if 'Year_macro' in master_df.columns:
        master_df = master_df.drop(columns=['Year_macro'])
        
    # MERGE 3: Master + NEA Macro
    master_df = pd.merge(master_df, df_nea, left_on='Year_Int', right_on='Year', how='left', suffixes=('', '_nea'))
    if 'Year_nea' in master_df.columns:
        master_df = master_df.drop(columns=['Year_nea'])

    print(f"Final master records: {len(master_df)}")
    
    # Validation
    missing_macro = master_df['GDP_Growth_Pct'].isna().sum() if 'GDP_Growth_Pct' in master_df.columns else 0
    missing_nea = master_df['National_Peak_Demand_MW'].isna().sum() if 'National_Peak_Demand_MW' in master_df.columns else 0
    print(f"Missing Macro values: {missing_macro}")
    print(f"Missing NEA values: {missing_nea}")
    
    # Sort for Time-Series logic
    master_df = master_df.sort_values(by=['Ticker', 'Year_Int']).reset_index(drop=True)
    
    # Calculate target variable: Free Cash Flow to Firm (FCFF) proxy if not already there
    # FCFF = Operating Profit - Tax + Depreciation - Capital Expenditure - Changes in NWC
    # For a simplified proxy (since full capex/NWC might be complex):
    # Operating Cash Flow Proxy = ProfitAfterTax + Depreciation
    if 'OperatingCashFlow_Proxy' not in master_df.columns:
        profit = master_df.get('ProfitAfterTax', 0)
        depr = master_df.get('Depreciation', 0)
        master_df['OperatingCashFlow_Proxy'] = profit + depr

    # Save to file
    master_df.to_csv("data/master_ml_dataset.csv", index=False)
    print("\nSuccessfully saved master dataset to data/master_ml_dataset.csv")

if __name__ == "__main__":
    main()
