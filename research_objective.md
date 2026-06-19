# Research Context: ML-Based FCF Forecasting & DCF Valuation for NEPSE Hydropower Firms

This file is a self-contained context document for an academic research project. It is intended to be pasted into any LLM session to bring it up to speed on the study design, data plan, and feature set without needing prior conversation history.

---

## 1. Research Title (working)

**Machine Learning vs. Traditional Forecasting of Free Cash Flow for Discounted Cash Flow Valuation: Evidence from NEPSE-Listed Hydropower Firms**

> Note: This study was originally scoped around NEPSE-listed *manufacturing* firms (cement, beverage, consumer goods — only ~16 listed companies). It has been **switched to the hydropower sector**, which has 105 NEPSE-listed companies, giving a much larger and more homogeneous panel. All methodology below reflects the hydropower version.

---

## 2. Researcher Background (for context/calibration)

- Lecturer at Herald College Kathmandu, teaching Big Data.
- Academic background: BBS (finance), IGNOU distance MCA, M.Ed. in Mathematics and Computer Science (Kathmandu University).
- ~5 years prior experience as a stockbroker.
- Pursuing PhD trajectory; primary research interest is Explainable AI (XAI) applied to financial markets, particularly NEPSE.
- Has submitted a related research proposal to a KU supervisor on LSTM/TFT forecasting + SHAP/LIME-based XAI for NEPSE.
- Prefers rigorous, example-driven, technically precise explanations.

---

## 3. Research Gap

Most Nepali valuation studies:
- Use historical growth assumptions
- Use ratio analysis
- Use basic DCF

Almost none:
- Forecast FCF using machine learning
- Compare ML against traditional forecasting methods
- Study NEPSE-listed **hydropower** firms specifically, despite hydropower being one of the largest and most homogeneous sectors on the exchange (105 listed companies)

**Stated gap:** There is limited evidence on whether machine learning models improve Free Cash Flow forecasting and DCF valuation accuracy for NEPSE-listed hydropower firms — a sector with structurally distinct, nonlinear cash flow dynamics (construction-phase capex, regime shift at commercial operation date, seasonal hydrology-driven revenue) that traditional linear forecasting methods are poorly suited to capture.

---

## 4. Research Questions

- **RQ1:** Can ML models forecast FCF more accurately than traditional statistical methods for NEPSE-listed hydropower firms?
- **RQ2:** Which variables most influence future FCF in this sector (financial, operational, and macro/hydrology)?
- **RQ3:** How does ML-based DCF valuation differ from traditional DCF valuation, and which is closer to actual market capitalization?

---

## 5. Why Hydropower Instead of Manufacturing (rationale, for methodology/justification section)

1. **Sample size:** 105 listed companies vs. ~16 for manufacturing — enables a real panel rather than a thin one.
2. **Homogeneity:** Hydropower firms mostly sell to a single buyer (Nepal Electricity Authority, NEA) under broadly similar PPA structures, unlike manufacturing which spans cement/beverage/consumer goods with very different cost structures. A more homogeneous panel helps ML models generalize.
3. **Genuine nonlinearity in FCF:** Manufacturing FCF is roughly linear (steady operating cash flow minus modest maintenance capex) — exactly the regime where linear regression already performs well, weakening the case for ML. Hydropower FCF is structurally nonlinear: large negative FCF during construction (debt-funded capex), a sharp regime shift at COD (commercial operation date), and strong seasonality (wet vs. dry season generation). This gives a real economic mechanism for why tree-based/ML models should outperform linear models — not just "ML is fashionable."
4. **Richer, sector-specific predictor set:** installed capacity, plant load factor, years since COD, hydrology year-type, royalty regime, PPA tariff structure — none of which has an analogue in the manufacturing version, and which produce a much richer SHAP/interpretability narrative.

---

## 6. Key Methodological Risks / Decisions (already discussed, decisions logged)

- **Pre-COD vs. post-COD years:** Pre-COD FCF is mechanically just "large negative number driven by capex disbursement schedule" — not genuinely forecastable operating cash flow. Including it risks inflating apparent model accuracy (predicting "large negative" is easy) while diluting the operating-FCF story.
  - **Decision: Include all years (bigger N)** — user has explicitly chosen this over post-COD-only, accepting the tradeoff above. This should be disclosed as a limitation, and a pre/post-COD flag must be retained in the panel so it can be used as a control variable or basis for a robustness-check subsample.
- **Unbalanced panel:** NEPSE hydro listings span IPOs from the early 2000s through 2024–2025. Some companies will contribute ~12–14 years of data, others only 2–3. This must be handled explicitly (e.g., as an unbalanced panel in the econometric sense), not treated as a data inconvenience to paper over.
- **Terminal value horizon:** Hydropower PPAs/licenses have finite terms (commonly 30–35 years). A Gordon Growth (perpetuity) terminal value is theoretically questionable for an asset with a finite license term. A finite-horizon terminal value approach (or explicit license-term-bounded DCF) is more defensible than infinite-horizon Gordon growth, and should be used or at least discussed as the methodologically correct alternative in Step 13/14.
- **Data frequency: Annual, not quarterly.** Reasoning:
  - NEPSE quarterly filings are unaudited and typically only disclose top-line P&L (revenue, net profit) — not full balance sheet/cash flow detail needed for debt ratio, current ratio, ROA, ROE, asset turnover, etc.
  - Revenue seasonality (wet/dry season) is already captured more directly and cleanly via the PLF / seasonal generation split feature — quarterly P&L would be a noisier, redundant proxy for a signal already captured better elsewhere.
  - CapEx/working capital don't move in interpretable quarterly chunks for project-financed construction (disbursements follow loan covenant schedules, not calendar quarters).
  - The unit of analysis (FCF formula, train/test split, DCF horizon) is firm-*year* — mixing in quarterly predictors would create a frequency mismatch requiring awkward re-aggregation.
  - Optional forward-looking note for the paper: quarterly revenue *could* be used in future work to construct a more precise wet/dry seasonal split, but is not used here due to disclosure inconsistency across 105 firms and the annual nature of the FCF target.
- **Beta/WACC estimation:** NEPSE hydro counters are thinly traded; NEPSE-implied beta is likely noisy across 105 firms. Consider industry-average beta as an alternative, and explicitly flag this as a limitation if firm-specific beta is used.
- **Disclosure completeness varies a lot across 105 firms** (older/larger listings like Chilime, Butwal Power, Arun Valley tend to have richer annual reports; many smaller recent IPOs may only disclose bare income statement/balance sheet figures). Recommend tracking a "disclosure completeness" flag per company, usable as a control variable or basis for a robustness-check subsample.

---

## 7. Sample & Period

- **Sample:** 105 NEPSE-listed hydropower companies (full list held by researcher).
- **Period:** 2012–2025 (consistent with original manufacturing-sector design; actual usable years per firm vary based on listing date/COD).
- **Panel structure:** Unbalanced panel, company × year, all years included (pre- and post-COD).

---

## 8. Methodology Overview

### 8.1 Target Variable
**FCF** = EBIT(1 − Tax Rate) + Depreciation & Amortization − CapEx − ΔWorking Capital
where ΔWC = WC(t) − WC(t−1)

### 8.2 Train-Test Split
Chronological (never random, to preserve time-series structure).
- Baseline plan: Train 2012–2021, Test 2022–2025 — **needs re-validation against actual firm-level data availability**, since many hydro firms IPO'd or reached COD well after 2012, which may leave the training set thin/unbalanced for those firms.

### 8.3 Baseline (Traditional) Models
1. Historical mean
2. Linear regression
3. ARIMA (optional)

### 8.4 Machine Learning Models
1. Random Forest (baseline ML)
2. XGBoost (expected strongest performer)
3. LightGBM (optional)
4. LSTM (only if sufficient observations after panel construction)

### 8.5 Evaluation Metrics
- MAE = (1/n) Σ |Actual − Predicted|
- RMSE = √[(1/n) Σ (Actual − Predicted)²]
- MAPE = |Actual − Predicted| / Actual

### 8.6 Interpretability
SHAP values applied to the best-performing model(s) to identify key FCF drivers — financial, operational, and macro/hydrology variables.

### 8.7 Statistical Testing
- Paired t-test and/or Wilcoxon signed-rank test
- Compares forecasting error (ML vs. traditional) for statistical significance
- Hypothesis: ML produces significantly lower forecasting error than traditional methods

### 8.8 DCF Valuation Stage
1. Forecast FCF for next 5 years using best ML model and using traditional method (parallel tracks).
2. Enterprise Value: EV = Σ [FCF(t) / (1 + WACC)^t] + Terminal Value
3. Terminal Value — **use finite-horizon approach bounded by PPA/license term where feasible**, rather than unconditional Gordon Growth perpetuity, given finite license terms in this sector. Gordon Growth TV = FCF(n+1) / (WACC − g) may still be reported as a comparison/robustness case.
4. **Validation:** Compare both DCF outputs (ML-based vs. traditional-based) against actual NEPSE market capitalization. Whichever is closer is the headline empirical finding for RQ3.

---

## 9. Full Feature List

### 9.1 Target Variable
| Feature | Formula |
|---|---|
| FCF (dependent variable) | EBIT(1 − T) + D&A − CapEx − ΔWorking Capital |

### 9.2 Panel Identity / Structural Fields (not predictors — used for ID, splitting, controls)
| Field | Purpose |
|---|---|
| Company name / ticker | Panel ID |
| Year | Panel ID |
| COD (commercial operation date) | Defines pre/post-COD flag |
| Pre/Post-COD flag | Regime control; basis for robustness-check subsample |
| Installed capacity (MW) | Scale control; PLF calculation |
| NEPSE listing date | Defines start of market-cap validation data |
| License type & term (years) | Terminal value horizon |
| Disclosure completeness flag | Data quality control; robustness-check basis |

### 9.3 Core Financial Predictors (firm-level, from financial statements)
| Feature | Formula |
|---|---|
| Revenue growth | (Revₜ − Revₜ₋₁) / Revₜ₋₁ |
| EBIT margin | EBIT / Revenue |
| Net profit margin | Net Income / Revenue |
| Debt ratio | Total Debt / Total Assets |
| Current ratio | Current Assets / Current Liabilities |
| ROA | Net Income / Total Assets |
| ROE | Net Income / Total Equity |
| Asset turnover | Revenue / Total Assets |
| Effective tax rate | Tax Expense / Pre-tax Income |
| Interest burden / coverage | Interest Expense / EBIT |

> **Data frequency note:** All of the above are **annual** figures, sourced from audited annual reports. Quarterly data is deliberately not used (see Section 6 for reasoning) — NEPSE quarterly filings are unaudited and lack full balance-sheet/cash-flow detail needed for most of these ratios.

### 9.4 Lag and Engineered (Time-Series) Features
| Feature | Construction |
|---|---|
| Revenue lag (t−1) | Revₜ₋₁ |
| FCF lag (t−1) | FCFₜ₋₁ |
| Revenue growth lag (t−1) | RevGrowthₜ₋₁ |
| EBIT growth | (EBITₜ − EBITₜ₋₁) / EBITₜ₋₁ |
| 3-year rolling avg revenue growth | mean(RevGrowth, t−2:t) |
| 3-year rolling avg EBIT margin | mean(EBIT margin, t−2:t) |
| Years since COD | t − COD year (proxies lifecycle/ramp-up stage) |

### 9.5 Hydropower-Specific Operational Predictors (sector differentiator)
| Feature | Source / Notes |
|---|---|
| Units generated (GWh/year) | Annual report, if disclosed |
| Plant load factor (PLF) | Generation / (Capacity × 8760 hrs) |
| Wet vs. dry season generation split | Annual report, or proxy via hydrology index |
| PPA tariff — wet season rate | Annual report / PPA disclosure |
| PPA tariff — dry season rate | Annual report / PPA disclosure |
| Tariff escalation status (active/expired) | PPA terms — many escalate fixed % for first 8–10 yrs, then flatten |
| Take-or-pay vs. take-and-pay flag | PPA terms |
| Royalty paid (capacity + energy) | Annual report note — per Electricity Act |

### 9.6 Macroeconomic / Sector-Level Predictors (merged in, not collected per-company)
| Feature | Source |
|---|---|
| GDP growth | NRB / World Bank |
| Inflation | NRB / World Bank |
| Interest rate | Nepal Rastra Bank (NRB) |
| Hydrology / rainfall index (replaces GDP as lead driver for this sector) | Department of Hydrology and Meteorology (DHM), or NEA annual report system-wide hydrology commentary |
| NEA average bulk purchase tariff | NEA annual report |

### 9.7 Validation-Stage Data (used in DCF validation step, not as model predictors)
| Feature | Purpose |
|---|---|
| Market capitalization (year-end) | Benchmark for ML-DCF vs. traditional-DCF comparison |
| Share price history | Optional — beta estimation (noisy for thinly-traded hydro counters) |
| WACC inputs (risk-free rate, ERP, beta, cost of debt) | Discounting both DCF variants |
| Terminal growth rate / license-term horizon | Finite-horizon TV calculation given PPA/license expiry |

---

## 10. Data Sources

| Data type | Source |
|---|---|
| Financial statements | Company annual reports (PDF); merolagani.com, sharesansar.com, company IR pages |
| COD, installed capacity, license terms | Annual report MD&A section; Department of Electricity Development (DoED) license database |
| PPA terms | Annual report disclosures (full PPA documents are generally not public) |
| Generation data / PLF | Annual report; sometimes NEA's own annual report (lists IPP generation by plant) |
| Royalty paid | Annual report — usually a separate line item or note |
| Macroeconomic data | Nepal Rastra Bank (NRB) data portal, World Bank |
| Hydrology / rainfall | Department of Hydrology and Meteorology (DHM); NEA annual report hydrology commentary |
| Market capitalization | NEPSE website, sharesansar, merolagani |

**Extraction method:** Manual extraction from annual reports (researcher's choice, given at 105 companies × up to 14 years — acknowledged as a large effort; ~700–1,000+ firm-years × ~10-15 fields).

---

## 11. Proposed Paper Structure

1. Introduction
2. Literature Review
3. Research Gap
4. Methodology
   - Research Design
   - Sample Selection
   - Data Sources
   - Variable Definitions
   - Model Specification (traditional + ML)
   - Train-Test Split
   - Evaluation Metrics
   - DCF Valuation Framework
   - Statistical Testing
   - Interpretability (SHAP)
5. Results
6. SHAP Analysis
7. DCF Valuation Results
8. Discussion
9. Conclusion
10. References (APA)

---

## 12. Open Items / Not Yet Finalized

- Final train/test split years — needs validation against actual per-firm data availability once the panel is constructed (many hydro firms post-date 2012 for listing/COD).
- Whether to also report a post-COD-only subsample as a robustness check, given the decision to include all years in the primary analysis.
- Exact hydrology index/proxy to use (DHM rainfall data vs. NEA system-wide generation shortfall commentary) — not yet selected.
- Beta estimation approach (firm-specific NEPSE beta vs. industry-average beta) — not yet decided.
- Full list of 105 company tickers — held by researcher, not yet integrated into a structured tracker file.