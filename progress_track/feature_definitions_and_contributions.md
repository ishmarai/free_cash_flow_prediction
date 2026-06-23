# Data Dictionary & Theoretical Contribution Guide

This document catalogs every feature present in the `data/master_ml_dataset.csv` panel data. It provides the definition of each variable and its theoretical contribution to the Machine Learning Free Cash Flow (FCF) forecasting model. This will be highly useful for the "Methodology" and "Results" sections of the research paper.

---

## 1. The Target Variable
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`OperatingCashFlow_Proxy`** | Profit After Tax (PAT) + Depreciation. | **The Target ($Y$)**. This serves as our proxy for Free Cash Flow to Firm (FCFF). Accurately forecasting this over a 5-year horizon is the core objective of the Intrinsic Valuation model. |

---

## 2. Core Financial Statements (The Baseline)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`Revenue`** | Gross income from energy sales to NEA. | The absolute size of cash generation. |
| **`EBIT`** | Earnings Before Interest & Taxes. | Measures pure operational profitability before bank debt is factored in. |
| **`PAT`** | Profit After Tax. | The final bottom-line profit available to equity shareholders. |
| **`CapEx`** | Capital Expenditure. | Heavy during construction, drops post-COD. Highly predictive of negative cash flows. |
| **`Change_in_WC`** | Change in Working Capital. | Captures short-term liquidity constraints. |
| **`Depreciation_Expense`** | Non-cash accounting expense. | Added back to PAT to find true cash generation. Crucial for FCF. |
| **`Interest_Expense`** | Cost of servicing bank debt. | Expected to be massive post-COD and slowly decline as the loan amortizes. |

---

## 3. Engineered Lifecycle Variables (The Temporal Anchors)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`COD_Year`** | Commercial Operation Date Year. | Marks the exact pivot point from capital burn (construction) to cash generation. |
| **`Years_Since_COD`** | Count of years since operations began. | **Highly Critical**. Allows the ML model to learn the non-linear debt repayment curve. Cash flows naturally surge 10-12 years after COD once bank consortiums are paid off. Also flags when the 3% PPA tariff escalation cap is reached. |
| **`Pre_Post_COD`** | Binary flag (0 = Construction, 1 = Active). | Prevents the ML model from treating zero-revenue construction years as bankruptcies. |

---

## 4. Financial Ratios (The Quality Metrics)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`EBIT_Margin` & `Net_Profit_Margin`** | Profitability as a percentage of Revenue. | Dictates how efficiently the plant translates water into profit. |
| **`Debt_Ratio`** | Total Debt / Total Assets. | Measures leverage risk. High debt restricts FCF due to massive interest burdens. |
| **`ROA` & `ROE`** | Return on Assets / Equity. | Standard corporate finance benchmarks for management efficiency. |

---

## 5. Time-Series Dynamics (The Momentum Indicators)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`Revenue_Lag1` & `FCF_Lag1`** | Last year`s Revenue and Cash Flow. | Hydropower relies on autoregressive momentum (a good year is likely followed by a good year unless hydrology shocks occur). |
| **`Rolling3_Avg_Rev_Growth`** | 3-Year moving average of revenue growth. | Smooths out single-year hydrology anomalies (like floods) to find the true underlying growth trend. |

---

## 6. Operational Physics (The Physical Constraints)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`Installed_Capacity_MW`** | Maximum plant size. | The hard upper limit on revenue potential. |
| **`PLF`** | Plant Load Factor (Implied). | **Highly Critical**. Measures hydrological efficiency. A drop in PLF immediately destroys FCF. The ML model will heavily weigh this to understand climate/river risks. |
| **`License_Term_Years`** | Remaining legal lifespan (max 35 years). | Represents the Terminal Value cutoff point. A plant with 5 years left is fundamentally worth less than a newly licensed plant. |
| **`PPA_Tariff_Wet` / `Dry`** | Base selling price per unit. | Directly dictates the revenue scaling multiplier. |

---

## 7. Macroeconomic Risk (The Systemic Shocks)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`GDP_Growth`** | National economic growth. | High GDP correlates strongly with electricity demand, ensuring NEA buys all generated power without dispatch curtailment. |
| **`Inflation`** | National Consumer Price Index. | Drives up O&M (Operations & Maintenance) costs, squeezing profit margins. |
| **`Interest_Rate`** | Weighted average lending rate. | **Highly Critical**. A spike in national interest rates immediately increases the company`s debt-servicing cost, directly destroying Free Cash Flow. |

---

## 8. NEA Grid Dynamics (The Dispatch Risk)
| Feature | Definition | Theoretical Contribution to Results |
| :--- | :--- | :--- |
| **`Total_IPP_Generation_GWh`** | Total supply from all private plants. | Indicates competition. If supply exceeds demand during the wet season, the grid may spill water (curtailment). |
| **`National_Peak_Demand_MW`** | Total national demand limit. | The ceiling of the market. |
| **`Power_Import_From_India_GWh`** | Energy bought from India. | A proxy for systemic deficit. High imports mean domestic plants have guaranteed dispatch (low curtailment risk). |
