# 🤖 Machine Learning Co-Author Guide
**Objective:** Forecasting Free Cash Flow to Firm (FCFF) and Intrinsic Valuation using Machine Learning vs. Traditional DCF.

Welcome to the ML phase! The primary researcher has handled all the complex financial accounting, operational physics, and macroeconomic data gathering. The master dataset (`data/master_ml_dataset.csv`) is clean, flat, and ready for modeling. 

Because your background is in Data Science and not Corporate Finance, this guide breaks down exactly what the financial variables mean, what you are trying to predict, and the required visual outputs for the research paper.

---

## 1. The Dataset & The Objective
**File:** `data/master_ml_dataset.csv`
**Format:** A 16-year panel data (Time-Series Cross-Sectional) covering 105 specific Hydropower Companies.

### Data Dictionary: Features ($X$) and Target ($Y$)
To assist in your feature engineering and modeling, here is the exact breakdown of the variables in the dataset:

| Category | Variable Name | Role | Description |
| :--- | :--- | :--- | :--- |
| **Target Variable** | `OperatingCashFlow_Proxy` | **Target ($Y$)** | A proxy for FCFF (Profit After Tax + Depreciation). This is what you are predicting over the next 5 years. |
| **Financial State** | `Revenue` | Feature ($X$) | Top-line energy sales. Dictated by the PPA tariff and generation. |
| **Financial State** | `PaidUpCapital` | Feature ($X$) | Equity base of the company. |
| **Financial State** | `FixedAssets` | Feature ($X$) | The physical plant value on the balance sheet. |
| **Financial State** | `StLiabilities` | Feature ($X$) | Short-term debt/liabilities. |
| **Operational** | `Installed_Capacity_MW` | Feature ($X$) | Maximum theoretical power output of the plant. |
| **Operational** | `PLF` | Feature ($X$) | Plant Load Factor (Efficiency). Highly critical feature. |
| **Operational** | `License_Term_Years` | Feature ($X$) | Number of years until the plant reverts to the government. |
| **Macroeconomic** | `GDP_Growth_Pct` | Feature ($X$) | Systemic economic growth metric. |
| **Macroeconomic** | `Inflation_Rate_Pct` | Feature ($X$) | Inflation impacts O&M costs and interest rates. |
| **Macroeconomic** | `National_Peak_Demand_MW` | Feature ($X$) | Systemic demand proxy indicating grid saturation limits. |

---

## 2. The Modeling Workflow

### Step A: Train/Test Split Strategy
Because this is Panel Data, **do not use random train_test_split**. You will introduce temporal data leakage.
*   **Strategy:** Train the model on historical years (e.g., 2010–2022) and Test/Validate on the unseen future years (e.g., 2023–2025). 

### Step B: The Machine Learning Models
You need to implement and compare a few distinct architectures to see which handles tabular financial time-series best:
1.  **XGBoost / LightGBM:** Generally the best-in-class for structured tabular financial data. Highly recommended for this dataset.
2.  **Random Forest Regressor:** Excellent for capturing non-linear operational constraints without overfitting as easily as gradient boosters.

*(Note: We are intentionally avoiding Deep Learning/LSTMs as they tend to severely overfit tabular datasets of this size and lack the necessary interpretability required by finance journal reviewers).*

---

## 3. The Baseline: "Old Valuation Methods" (5-Year DCF)
To prove our ML approach is valuable for the research paper, we must compare it against the traditional way finance professionals do things: **The Discounted Cash Flow (DCF) Model**.

*   **Valuation Horizon (5 Years):** While infrastructure projects sometimes use 10-year explicit forecasts, we have explicitly chosen a **5-year forecast horizon** (plus a Terminal Value). 
    *   *Why?* Because predicting 10 years into the future using Machine Learning introduces compounding error rates that degrade the model`s accuracy. A 5-year explicit horizon provides a perfect, realistic apples-to-apples baseline comparison between human-traditional forecasting and ML-forecasting.
*   **Your Task:** Write a standard Python script that calculates a Traditional 5-Year DCF. 
    *   Take the historical 3-year average of a company`s Cash Flow growth. 
    *   Project that straight-line average into the future for exactly 5 years. 
    *   Calculate the Terminal Value at Year 5.
    *   Discount all cash flows back to Present Value using a standard discount rate (e.g., 10%). 
*   **The Goal:** Show how the "straight-line" traditional DCF fails to capture macro-economic shocks, whereas your ML model dynamically adjusts 5-year cash flows based on macroeconomic variables!

---

## 4. Required Figures for the Research Paper
Once the models are trained, you must generate the following publication-ready plots for the final paper:

### 📊 Plot 1: Actual vs. Predicted FCFF (Line Chart)
*   **What it is:** A time-series line chart for 3 specific, well-known companies (e.g., "CHCL", "API", "UPPER").
*   **Visual:** The X-axis is Time. The Y-axis is Cash Flow. Show the actual historical cash flows, and then show the ML prediction path vs. the Traditional DCF path over a 5-year window.

### 📊 Plot 2: Model Accuracy Comparison (Bar Chart)
*   **What it is:** A bar chart comparing the Error Rates (RMSE or MAE).
*   **Visual:** Compare XGBoost, Random Forest, and the Traditional DCF model side-by-side to definitively prove which method is most accurate.

### 📊 Plot 3: Feature Importance Explainer (SHAP Summary Plot)
*   **What it is:** Reviewers want to know *why* the ML model made a prediction. It cannot be a black box.
*   **Visual:** Generate a SHAP (SHapley Additive exPlanations) beeswarm plot. It will visually prove to finance reviewers that operational physics (`PLF`) and macroeconomics (`GDP_Growth`) significantly impact valuation!

### 📊 Plot 4: Macro-Shock Scenario Analysis
*   **What it is:** A sensitivity graph. 
*   **Visual:** Pick one test company. Show how your ML model changes its 5-year cash flow prediction if `Inflation_Rate_Pct` suddenly spikes to 15% versus if it stays flat at 5%. 

---

**Next Steps for You:** Create a Jupyter Notebook in this `machine_learning/` directory, load `../data/master_ml_dataset.csv`, and begin the EDA and model training!
