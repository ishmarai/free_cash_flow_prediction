import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def log_linear_impute(df, col_name):
    known = df.dropna(subset=[col_name]).copy()
    missing = df[df[col_name].isna()].copy()
    
    if missing.empty:
        return df
        
    X_train = known[["Year"]].values
    y_train = np.log(known[col_name].values)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    X_missing = missing[["Year"]].values
    y_pred_log = model.predict(X_missing)
    y_pred = np.exp(y_pred_log)
    
    df.loc[df[col_name].isna(), col_name] = y_pred
    return df

def main():
    print("Loading raw unimputed data...")
    df = pd.read_csv("data/nea_macro_features_raw.csv")
    
    cols_to_impute = [
        "Total_IPP_Generation_GWh",
        "Power_Import_From_India_GWh",
        "National_Peak_Demand_MW"
    ]
    
    for col in cols_to_impute:
        df = log_linear_impute(df, col)
        df[col] = df[col].round(2)
        
    df.to_csv("data/nea_macro_features_imputed.csv", index=False)
    print("Saved imputed data to data/nea_macro_features_imputed.csv")

if __name__ == "__main__":
    main()
