# Quantium Data Analytics - Retail Trial Store Assessment (Task 2)

An end-to-end data analytics and experimental analysis project evaluating the performance of new trial store layouts for **Quantium**. This project uses Python to benchmark trial store performance against dynamically scaled control stores to prove incremental uplift in sales and customer foot traffic.

---

## 📌 Business Case & Objective

Julia, our Category Manager, wants to evaluate whether recent layout changes in **three trial stores (Stores 77, 86, and 88)** led to a meaningful increase in sales, customer traffic, and transactions during the 3-month trial period (**February 2019 – April 2019**).

Because stores naturally vary in size and baseline sales volume, directly comparing raw numbers introduces significant bias. The objective of this project was to:
1. **Identify the single best matching Control Store** for each Trial Store based on pre-trial historical similarity (using Correlation and Magnitude metrics).
2. **Normalize (scale) historical performance** so control baselines directly mirror trial store expectations.
3. **Measure the statistical Uplift (%)** in Revenue, Customers, and Transactions during the trial period.

---

## 🛠️ Methodology & Engineering Architecture

### 1. Control Store Matching (Pre-Trial Phase: Jul 2018 – Jan 2019)
To find the ideal control store for each trial store, we evaluated two key historical metrics:
* **Pearson Correlation:** Assesses how closely two stores' monthly performance trends move together over time.
* **Magnitude Distance:** Measures how similar two stores are in absolute scale.

Combining these into an **Ultimate Match Score**, we identified the optimal store pairs:
* **Trial Store 77** 🤝 **Control Store 233**
* **Trial Store 86** 🤝 **Control Store 138**
* **Trial Store 88** 🤝 **Control Store 7**

---

### 2. Baseline Normalization (Scaling Factor)
Since control stores differ slightly in baseline magnitude, we calculated a pre-trial scaling ratio:

$$\text{Scaling Factor} = \frac{\sum \text{Trial Store Pre-Trial Metric}}{\sum \text{Control Store Pre-Trial Metric}}$$

Applying this factor to the control store’s trial period data generated a **counterfactual baseline**: *“What would the trial store have achieved if no store layout changes were implemented?”*

---

### 3. Uplift Evaluation
The incremental impact was calculated as the percentage difference between actual trial performance and scaled control performance:

$$\text{Uplift (\%)} = \left( \frac{\text{Trial Actual} - \text{Control Scaled}}{\text{Control Scaled}} \right) \times 100$$

---

## 📊 Key Results & Key Findings

All three trial stores demonstrated **clear, positive performance uplift** driven by layout changes:

* **Store 77 Pair (Control: 233):**
  * **Revenue:** Skyrocketed by **+36.65%** in March 2019 and **+62.31%** in April 2019.
  * **Customers:** Foot traffic increased by **+31.6%** to **+42.7%** over the same period.
* **Store 86 Pair (Control: 138):**
  * Immediate early success with a **+26.03%** revenue uplift in February 2019 and sustained customer growth (+28.75%).
* **Store 88 Pair (Control: 7):**
  * Steady, reliable growth across all metrics, peaking in April 2019 with a **+19.04%** revenue boost and **+18.26%** increase in total transactions.

---

## 📁 Repository Structure

```text
├── qvi_data.csv                 # Raw dataset (Transactions & Customer Info)
├── trial_period.py              # Main data pipeline script (Preprocessing, Scaling, Plotting)
├── charts/                      # Output directory containing high-resolution PNG visualizations
│   ├── revenue_77_vs_233.png
│   ├── customers_77_vs_233.png
│   └── ...
└── README.md                    # Project documentation


