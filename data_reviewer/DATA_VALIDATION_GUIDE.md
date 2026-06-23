# 📊 Data Validation & Purity Guide

**Attention Reviewers / Co-Authors:**
Before proceeding to the Machine Learning and Free Cash Flow (FCF) forecasting phase, this dataset requires a manual spot-check to ensure absolute data purity, zero mathematical hallucination, and structural integrity.

This guide outlines exactly what you need to verify.

---

## 1. Operational Data Validation
**Target File:** `data/operational_features.csv`
**Source Documents Required:** Individual Company Annual Reports (e.g., NGPL, API, CHCL)

### ✅ Task 1: Verify Installed Capacity
The `Installed_Capacity_MW` was extracted using a fuzzy-match algorithm connecting NEPSE Tickers to the official Department of Electricity Development (DoED) licensing dataset.
*   **Action**: Select a random sample of 5–10 tickers. Download their latest Annual Report (Prativedan) or IPO Prospectus.
*   **Check**: Does the `Installed_Capacity_MW` listed in the CSV exactly match the capacity stated in the "Project Profile" or "Chairman`s Statement" of the Annual Report?

### ✅ Task 2: Validate the Implied PLF (iPLF) Assumption
Because historical Plant Load Factor (PLF) data is rarely digitized or explicitly stated in Nepalese Annual Reports, we mathematically reverse-engineered it using the audited financial revenue constraint:
`iPLF = Revenue / (Capacity × 8760 hours × Rs. 6.00 Blended Tariff)`

*   **Action**: Find an Annual Report in your sample that explicitly states its physical generation (e.g., "This year, the plant generated 25,000,000 Units (kWh)").
*   **Check**: Calculate their actual PLF: `Actual Units / (Capacity_kW × 8760)`. Compare this actual physical PLF to the `PLF` column in our dataset. They should be highly correlated, proving that the Rs. 6.00/kWh proxy cleanly absorbs the operational reality.

---

## 2. Financial Accounting Data Validation
**Target File:** `data/financial_statement_features.csv`
**Source Documents Required:** Individual Company Audited Financial Statements

Our financial panel dataset spans 16 years (2010–2025). The base values (Revenue, Paid-Up Capital, Net Fixed Assets, EPS) form the backbone of the FCF prediction algorithms.

*   **Action**: Pick 3 companies at random. Choose one recent year (e.g., 2023/24) and one older year (e.g., 2015/16).
*   **Check**: Open the audited Balance Sheet and Profit & Loss (P&L) statements for those specific years. Cross-reference 3 key variables:
    1.  `Revenue` (Energy Sales)
    2.  `PaidUpCapital`
    3.  `FixedAssets` / `NetFixedAssets`
*   *Note: Our dataset records financial values in Rs. `000s (Thousands). Ensure you account for this scale when reading the absolute numbers in the Annual Report.*

---

## 3. Macroeconomic Data Review Guide

**Objective:** Verify the integrity and accuracy of the extracted 16-year macroeconomic panel (2010–2025) before it is merged into the main ML-based Free Cash Flow forecasting model. 

### Files to Review
*   **The Final Dataset:** `data/macroecomics_features.csv`
*   **The Source Files:** All files located in the `nrb_reports/` directory.

### What Needs to be Checked
The dataset contains the following critical macroeconomic and systemic features mapped against the year:

From `macroecomics_features.csv`:
1.  **`GDP_Growth`** (Source: "Real GDP at Producers/Purchasers Price")
2.  **`Inflation`** (Source: "National Consumer Price Index")
3.  **`Interest_Rate`** (Source: "Weighted Average Lending Rate" & "Interbank Transaction Rate")

From `nea_macro_features.csv` (and `nea_macro_features_imputed.csv`):
4.  **`Total_IPP_Generation_GWh`** (Source: "Power Purchase from IPPs")
5.  **`Power_Import_From_India_GWh`** (Source: "Power Purchase from India" - Hydrology proxy)
6.  **`National_Peak_Demand_MW`** (Source: "National Peak Demand")

#### Key Verification 1: Fiscal Year Alignment
The Nepal Rastra Bank (NRB) reports in Nepalese Fiscal Years (e.g., `2012/13`). In our dataset, this has been mapped to the ending calendar year (e.g., `2013`). 
*   **Task:** Verify that the data mapped to `2013` in the CSV correctly corresponds to the `2012/13` column in the NRB reports.

#### Key Verification 2: Random Sampling Check
The core data (2013–2025) was extracted iteratively by overwriting provisional numbers with the latest revised figures from the newest reports. 
*   **Task:** Pick 3 random years between 2013 and 2025. 
*   **Action:** Open `Macroeconomic-Indicators-of-Nepal-2025-December.xlsx` (or the 2024/2023 equivalents). 
    *   Go to **Table 3** to verify GDP Growth and Inflation.
    *   Go to **Table 19** to verify the Interest Rate (Weighted Average Lending Rate).
*   **Success Criteria:** The numbers in the CSV should perfectly match the spreadsheet.

#### Key Verification 3: The 2012/13 Statistical Rebasing Anomaly
Because NRB rebased their statistics in 2012/13, the standard Excel files cut off data prior to 2013. 
*   **Task:** Verify the 2010, 2011, and 2012 baseline figures.
*   **Action:** 
    *   Open the older PDFs: `Macroeconomic_Indicators_of_Nepal-2016-11...pdf` and `2018-11...pdf`.
    *   Check **Table 3** for GDP Growth and Inflation for `2009/10`, `2010/11`, and `2011/12`.
*   **Success Criteria:** The CSV values for 2010, 2011, and 2012 must perfectly match these older PDFs.

#### Key Verification 4: The 2010 & 2011 Interest Rate Proxy
NRB did not formally track the "Weighted Average Lending Rate" in this specific table structure prior to 2012. Rather than using mathematical guesswork (interpolation) to fill the gaps, we used true historical proxy data.
*   **Task:** Verify the 2010 and 2011 Interest Rate values (`7.13%` and `10.43%`).
*   **Action:** Open `Current_Macroeconomic_Situation_English-2011-06...xls`. 
    *   Go to the **"Interbank RAte"** sheet.
    *   Look for the **"Weighted Average Interbank Transaction Rate"** for the month of **July** (fiscal year-end).
*   **Success Criteria:** Verify that 7.13 corresponds to 2009/10 and 10.43 corresponds to 2010/11.

#### Key Verification 5: NEA Log-Linear Imputation Validation
Because the NEA Annual Reports lacked digitized systemic data from 2010 to 2015, we used an academic **Log-Linear OLS Backcasting** model to estimate `National_Peak_Demand_MW`, `Total_IPP_Generation_GWh`, and `Power_Import_From_India_GWh`.
*   **Action:** Review the original gaps in `data/nea_macro_features_raw.csv`. 
*   **Check:** Open `data/nea_macro_features_imputed.csv` and ensure the backward trajectory (2015 down to 2010) represents a smooth, logical exponential curve relative to the known 2016 values.

---

## 4. How to Report Findings
Write any discrepancy found in `progress_track/log.md` (or notify the primary researcher).
