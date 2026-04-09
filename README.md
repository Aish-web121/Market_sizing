Tesla Global EV Market Sizing (2024–2030)

A consulting-style market sizing model using IEA global EV data.

📌 1. Objective

This project builds a complete, industry-standard TAM–SAM–SOM market sizing model for the global Battery Electric Vehicle (BEV) market, with a focus on estimating Tesla’s achievable market share under three scenarios:

Bear
Base
Bull

The model is structured to reflect the approach used by consulting firms like McKinsey, BCG, and Bain.

📌 2. Data Sources

Primary Dataset:

International Energy Agency (IEA) – Global EV Outlook (2024)
(BEV unit sales, growth trends, regional penetration)

Secondary Validation Sources:

Tesla Annual Report (10-K)
Statista Global EV Sales Data

All raw data is stored exactly as downloaded for full transparency.

📌 3. Repository Structure
Market_Sizing/
│
├── 01_Data_Raw/                 # IEA raw datasets (untouched)
│     └── global_ev_raw.xlsx
│
├── 02_Data_Clean/               # Cleaned & standardized datasets
│     └── global_ev_cleaned.xlsx
│
├── 03_Model/                    # Final Excel model
│     └── Tesla_MarketSizing_Model.xlsx
│
├── 04_Outputs/                  # Charts, tables, and summary PDFs
│     ├── TAM_SAM_SOM_Charts.png
│     └── Summary_Table.pdf
│
└── README.md                    # Project documentation
📌 4. Modeling Framework
A. Global BEV Market Projection

The model uses IEA 2020–2024 BEV sales as the baseline, applying three fixed annual growth rates:

Scenario	Growth Rate	Logic
Bear	15%	Slow EV transition
Base	20%	Continuation of current trends
Bull	28%	Faster policy & tech adoption

Formula:

Market_t = Market_(t-1) × (1 + GrowthRate)
B. Tesla Market Share Projection
Scenario	Annual Change in Share
Bear	–2%
Base	0%
Bull	+2%

Formula:

Tesla_Share_t = Tesla_Share_(t-1) + AnnualChange
C. TAM–SAM–SOM Definition
TAM (Total Addressable Market):
Full global BEV market.
SAM (Serviceable Available Market):
Markets where Tesla currently sells (North America, Europe, China, selected APAC).
SOM (Serviceable Obtainable Market):
Tesla’s realistic capture based on projected market share.
📌 5. Key Outputs

The Excel model auto-generates:

🔹 BEV market projections (2024–2030)
🔹 Tesla forecasted unit sales
🔹 TAM–SAM–SOM numbers
🔹 Scenario-based growth comparisons
🔹 Professional charts for presentations

All outputs update when input assumptions change.

📌 6. How to Use the Model
Open 03_Model/Tesla_MarketSizing_Model.xlsx
Go to the Assumptions sheet
Modify:
Growth rates
Tesla starting market share
Scenario dropdown
All tables + charts update automatically

This keeps the model flexible, transparent, and consultant-friendly.
