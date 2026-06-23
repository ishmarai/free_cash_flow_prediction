import csv
import math

def parse_year(yr_str):
    """
    Parses fiscal year string 'YYYY/YY' to starting year integer.
    Example: '2022/23' -> 2022
    """
    try:
        return int(yr_str.split('/')[0])
    except Exception:
        return None

def to_float(val):
    """
    Parses a string value to float, handling 'NaN' or empty values.
    """
    if not val or val.strip().lower() == 'nan':
        return 0.0
    try:
        return float(val.strip())
    except ValueError:
        return 0.0

def safe_divide(num, denom):
    """
    Safely divides num by denom, returning float('nan') if denominator is zero or near zero.
    """
    if denom is None or math.isnan(denom) or abs(denom) < 1e-9:
        return float('nan')
    if num is None or math.isnan(num):
        return float('nan')
    return num / denom

def main():
    input_file = 'hydro.csv'
    output_file = 'hydro_features.csv'
    
    # 1. Read raw data
    print("Reading raw data from", input_file)
    firm_years = {}
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for row in reader:
            # We only use Q4 (annual) data
            if row[2] != '4':
                continue
            
            ticker = row[0]
            year_str = row[1]
            ds = row[3]
            
            key = (ticker, year_str)
            if key not in firm_years:
                firm_years[key] = row
            else:
                # Prioritize 'Audited' reports over 'Published'
                if ds == 'Audited':
                    firm_years[key] = row

    # 2. Group by ticker
    ticker_groups = {}
    for (ticker, year_str), row in firm_years.items():
        if ticker not in ticker_groups:
            ticker_groups[ticker] = []
        ticker_groups[ticker].append(row)
        
    # 3. Process each ticker's time series
    all_processed_rows = []
    
    for ticker, rows in ticker_groups.items():
        # Sort chronologically by starting year
        rows_sorted = sorted(rows, key=lambda x: parse_year(x[1]))
        
        # Determine COD Year (first year with positive Energy Sales)
        cod_year = None
        for r in rows_sorted:
            es = to_float(r[30])
            if es > 0.0:
                cod_year = parse_year(r[1])
                break
                
        # First pass: compute single-period features and working capital
        single_period_data = []
        for r in rows_sorted:
            year_str = r[1]
            yr_val = parse_year(year_str)
            
            # Extract basic financial variables
            paid_up = to_float(r[10])
            premium = to_float(r[11])
            reserves = to_float(r[12])
            lt_liab = to_float(r[13])
            gross_fa = to_float(r[15])
            accum_dep = to_float(r[16])
            net_fa = to_float(r[17])
            non_core = to_float(r[18])
            investments = to_float(r[19])
            wip = to_float(r[20])
            cash = to_float(r[21])
            receivables = to_float(r[22])
            adv_prep = to_float(r[23])
            inventory = to_float(r[24])
            ca = to_float(r[25])
            st_liab = to_float(r[26])
            def_liab = to_float(r[27])
            cl = to_float(r[28]) # TotalStLiabilities
            
            revenue = to_float(r[30]) # EnergySales
            ebit = to_float(r[37]) # OperatingProfit
            interest = abs(to_float(r[38])) # InterestIncomeExpense (absolute value)
            dep_exp = to_float(r[39]) # Period Depreciation Expense
            pbt = to_float(r[41])
            pat = to_float(r[43])
            
            # Calculations
            total_assets = net_fa + non_core + investments + wip + ca
            total_equity = paid_up + premium + reserves
            total_debt = lt_liab + cl
            working_capital = ca - cl
            
            # Effective Tax Rate
            tax_rate = 0.0
            if pbt > 0.0:
                tax_expense = pbt - pat
                if tax_expense > 0.0:
                    tax_rate = max(0.0, min(1.0, tax_expense / pbt))
            
            # Simple Ratios
            ebit_margin = safe_divide(ebit, revenue)
            net_profit_margin = safe_divide(pat, revenue)
            debt_ratio = safe_divide(total_debt, total_assets)
            current_ratio = safe_divide(ca, cl)
            roa = safe_divide(pat, total_assets)
            roe = safe_divide(pat, total_equity)
            asset_turnover = safe_divide(revenue, total_assets)
            interest_burden = safe_divide(interest, ebit)
            
            # Structural COD features
            if cod_year is not None:
                years_since_cod = yr_val - cod_year
                pre_post_cod = 1 if yr_val >= cod_year else 0
            else:
                years_since_cod = float('nan')
                pre_post_cod = 0
                
            single_period_data.append({
                'ticker': ticker,
                'year_str': year_str,
                'year_int': yr_val,
                'cod_year': cod_year,
                'years_since_cod': years_since_cod,
                'pre_post_cod': pre_post_cod,
                'revenue': revenue,
                'ebit': ebit,
                'pat': pat,
                'gross_fa': gross_fa,
                'wip': wip,
                'dep_exp': dep_exp,
                'interest': interest,
                'tax_rate': tax_rate,
                'working_capital': working_capital,
                'ebit_margin': ebit_margin,
                'net_profit_margin': net_profit_margin,
                'debt_ratio': debt_ratio,
                'current_ratio': current_ratio,
                'roa': roa,
                'roe': roe,
                'asset_turnover': asset_turnover,
                'interest_burden': interest_burden
            })
            
        # Second pass: compute lag and difference features
        for i, curr in enumerate(single_period_data):
            prev = single_period_data[i-1] if i > 0 else None
            
            # Check if previous year is consecutive
            is_consecutive = prev and (curr['year_int'] - prev['year_int'] == 1)
            
            if is_consecutive:
                # Revenue Growth
                rev_growth = safe_divide(curr['revenue'] - prev['revenue'], prev['revenue'])
                # EBIT Growth
                ebit_growth = safe_divide(curr['ebit'] - prev['ebit'], prev['ebit'])
                # CapEx = (GrossFA_t + WIP_t) - (GrossFA_t-1 + WIP_t-1)
                capex = (curr['gross_fa'] + curr['wip']) - (prev['gross_fa'] + prev['wip'])
                # Change in Working Capital
                dwc = curr['working_capital'] - prev['working_capital']
                
                # FCF = EBIT * (1 - Tax) + Depreciation - CapEx - Change in WC
                fcf = curr['ebit'] * (1 - curr['tax_rate']) + curr['dep_exp'] - capex - dwc
                
                revenue_lag1 = prev['revenue']
                revenue_growth_lag1 = prev.get('revenue_growth', float('nan'))
            else:
                rev_growth = float('nan')
                ebit_growth = float('nan')
                capex = float('nan')
                dwc = float('nan')
                fcf = float('nan')
                revenue_lag1 = float('nan')
                revenue_growth_lag1 = float('nan')
                
            curr['revenue_growth'] = rev_growth
            curr['ebit_growth'] = ebit_growth
            curr['capex'] = capex
            curr['dwc'] = dwc
            curr['fcf'] = fcf
            curr['revenue_lag1'] = revenue_lag1
            curr['revenue_growth_lag1'] = revenue_growth_lag1
            
        # Third pass: compute FCF_Lag1 and rolling averages
        for i, curr in enumerate(single_period_data):
            prev = single_period_data[i-1] if i > 0 else None
            is_consecutive = prev and (curr['year_int'] - prev['year_int'] == 1)
            
            if is_consecutive:
                fcf_lag1 = prev['fcf']
                # Try to get revenue growth lag 1 from prev
                curr['revenue_growth_lag1'] = prev['revenue_growth']
            else:
                fcf_lag1 = float('nan')
                curr['revenue_growth_lag1'] = float('nan')
                
            curr['fcf_lag1'] = fcf_lag1
            
            # Rolling 3-year averages (needs current and 2 previous consecutive years)
            r3_growth = float('nan')
            r3_ebit_margin = float('nan')
            if i >= 2:
                p1 = single_period_data[i-1]
                p2 = single_period_data[i-2]
                consec_3 = (curr['year_int'] - p1['year_int'] == 1) and (p1['year_int'] - p2['year_int'] == 1)
                if consec_3:
                    growths = [p2['revenue_growth'], p1['revenue_growth'], curr['revenue_growth']]
                    margins = [p2['ebit_margin'], p1['ebit_margin'], curr['ebit_margin']]
                    
                    # Filter out NaNs for mean calculation
                    valid_growths = [g for g in growths if not math.isnan(g)]
                    valid_margins = [m for m in margins if not math.isnan(m)]
                    
                    if len(valid_growths) == 3:
                        r3_growth = sum(valid_growths) / 3
                    if len(valid_margins) == 3:
                        r3_ebit_margin = sum(valid_margins) / 3
                        
            curr['rolling3_avg_rev_growth'] = r3_growth
            curr['rolling3_avg_ebit_margin'] = r3_ebit_margin
            
            all_processed_rows.append(curr)

    # 4. Write processed features to CSV
    output_headers = [
        'Ticker', 'Year', 'Year_Int', 'COD_Year', 'Years_Since_COD', 'Pre_Post_COD',
        'Revenue', 'EBIT', 'PAT', 'CapEx', 'Change_in_WC', 'Depreciation_Expense',
        'Interest_Expense', 'Tax_Rate', 'Working_Capital', 'FCF',
        'EBIT_Margin', 'Net_Profit_Margin', 'Debt_Ratio', 'Current_Ratio', 'ROA', 'ROE', 'Asset_Turnover',
        'Interest_Burden', 'Revenue_Growth', 'EBIT_Growth', 'Revenue_Lag1', 'FCF_Lag1',
        'Revenue_Growth_Lag1', 'Rolling3_Avg_Rev_Growth', 'Rolling3_Avg_Ebit_Margin'
    ]
    
    print("Writing features to", output_file)
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(output_headers)
        
        written_count = 0
        for row in all_processed_rows:
            # Only keep rows where target variable FCF is present
            if row['fcf'] is None or math.isnan(row['fcf']):
                continue
                
            # Map nan to empty string for clean CSV representation
            def clean_val(v):
                if v is None:
                    return ''
                if isinstance(v, float) and math.isnan(v):
                    return ''
                return v
                
            writer.writerow([
                row['ticker'],
                row['year_str'],
                clean_val(row['year_int']),
                clean_val(row['cod_year']),
                clean_val(row['years_since_cod']),
                row['pre_post_cod'],
                clean_val(row['revenue']),
                clean_val(row['ebit']),
                clean_val(row['pat']),
                clean_val(row['capex']),
                clean_val(row['dwc']),
                clean_val(row['dep_exp']),
                clean_val(row['interest']),
                clean_val(row['tax_rate']),
                clean_val(row['working_capital']),
                clean_val(row['fcf']),
                clean_val(row['ebit_margin']),
                clean_val(row['net_profit_margin']),
                clean_val(row['debt_ratio']),
                clean_val(row['current_ratio']),
                clean_val(row['roa']),
                clean_val(row['roe']),
                clean_val(row['asset_turnover']),
                clean_val(row['interest_burden']),
                clean_val(row['revenue_growth']),
                clean_val(row['ebit_growth']),
                clean_val(row['revenue_lag1']),
                clean_val(row['fcf_lag1']),
                clean_val(row['revenue_growth_lag1']),
                clean_val(row['rolling3_avg_rev_growth']),
                clean_val(row['rolling3_avg_ebit_margin'])
            ])
            written_count += 1
            
    print(f"Successfully wrote {written_count} rows to {output_file}.")

if __name__ == '__main__':
    main()
