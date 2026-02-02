## 📌 Project Overview
This project presents an end-to-end exploratory and analytical study of retail profit data across the UK. It focuses on identifying regional performance patterns, seasonal trends, and vendor contributions to overall profitability.

## 🔍 Workflow Highlights
- Data preparation and cleaning  
- Profit aggregation by month, region, location, and vendor  
- Statistical analysis, including confidence intervals and hypothesis testing  
- Interactive and static visualizations, including UK choropleth maps  

## 🛠️ Tech Stack
**Languages**: Python (Pandas, Matplotlib, Seaborn), SQL
**Tools**: Jupyter Notebook, Power BI, Excel

## 🎯 Objective
The goal of this analysis is to determine where profits are generated, when performance peaks, and which vendors contribute the most value—delivering insights to support data-driven business and strategic decisions.


---


The analysis focuses on answering key business questions:

- Which UK regions generate the highest total profit?
- How does profit vary across sales months?
- Which vendors contribute most to overall profitability?
- Is there a statistically significant difference between top and low-performing vendors?

The project follows a structured analytics pipeline, from raw data preparation to insight-driven visualizations.

---

## 🗂️ Project Structure

```text
.
├── 01_data_preparation.ipynb      # Data cleaning & preprocessing
├── 02_aggregation_tables.ipynb    # Aggregated profit tables
├── 03_exploratory_analysis.ipynb  # EDA & statistical analysis
│
├── plotting.py                    # Reusable plotting & stats functions
├── city_to_region.py              # City → UK region mapping
│
├── monthly_profit_report.csv      # Monthly profit summary
├── location_profit_report.csv     # Profit by store/location
├── vendor_report.csv              # Vendor contribution analysis
└── README.md
