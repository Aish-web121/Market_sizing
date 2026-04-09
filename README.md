Tesla Global EV Market Sizing (2024–2030)

A consulting-style market sizing model using IEA global EV data

1. Objective

This project builds a complete TAM–SAM–SOM market sizing model for the global Battery Electric Vehicle (BEV) market.
It estimates Tesla’s potential market share, deliveries, and revenue under three scenarios:

Bear
Base
Bull

The approach follows the structured modeling frameworks used by McKinsey, BCG, and Bain.

2. Data Sources
Primary Dataset
International Energy Agency (IEA) – Global EV Outlook 2024
(BEV sales, CAGR trends, regional penetration data)
Secondary Validation Sources
Tesla Annual Report (10-K)
Statista Global EV Market Data

All raw data is stored exactly as downloaded for transparency.

3. Repository Structure
Market_Sizing/
│
├── 01_Data_Raw/                 # Original IEA datasets
│     └── global_ev_raw.xlsx
│
├── 02_Data_Clean/               # Cleaned & standardized datasets
│     └── global_ev_cleaned.xlsx
│
├── 03_Model/                    # Final Excel model (scenario-driven)
│     └── Tesla_MarketSizing_Model.xlsx
│
├── 04_Outputs/                  # Charts, tables, and summary exports
│     ├── TAM_SAM_SOM_Charts.png
│     └── Summary_Table.pdf
│
└── README.md                    # Documentation
4. Modeling Framework
A. Global BEV Market Projection (TAM)

Using IEA 2020–2024 BEV sales as the baseline, projections are built using fixed annual growth rates:

Scenario	Growth Rate	Interpretation
Bear	15%	Slower EV adoption
Base	20%	Continuation of current global trends
Bull	28%	Accelerated policy and technology push

Formula

Market_t = Market_(t-1) × (1 + GrowthRate)
B. Tesla Market Share Projection (SOM)
Scenario	Annual Market Share Change
Bear	–2% per year
Base	0% (steady)
Bull	+2% per year

Formula

TeslaShare_t = TeslaShare_(t-1) + AnnualChange
C. TAM–SAM–SOM Definitions
TAM — Total Addressable Market
Entire global BEV market.
SAM — Serviceable Available Market
Regions where Tesla operates:
North America, Europe, China, and selected APAC markets.
SOM — Serviceable Obtainable Market
Tesla’s realistic achievable penetration in SAM based on scenario-driven market share.
5. Key Outputs

The Excel model automatically generates:

Global BEV projections (2024–2030)
Tesla delivery forecasts
Tesla revenue projections
Market share evolution
Scenario comparison tables
TAM–SAM–SOM summary
Clean, presentation-ready charts

All results update dynamically based on the assumptions sheet.

6. How to Use the Model
Open:
03_Model/Tesla_MarketSizing_Model.xlsx
Navigate to the Assumptions tab.
Modify:
BEV growth rates
Tesla starting market share
Scenario (Bear / Base / Bull)
View updated results in:
Projection tables
Scenario comparisons
TAM–SAM–SOM summary
Charts & outputs

The model is intentionally designed to be transparent, modular, and consultant-friendly.
