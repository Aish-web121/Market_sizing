
Tesla Global EV Market Sizing (2024–2030)

A structured, consulting-style market sizing model built using IEA global EV datasets.
The project estimates the size of the global BEV market and projects Tesla’s deliveries and revenue under three scenarios.

1. Objective

This project develops an industry-standard TAM–SAM–SOM market sizing model for the global Battery Electric Vehicle (BEV) market.
It forecasts:

Global BEV market size
Tesla delivery volumes
Tesla revenue
Tesla’s achievable market share

All projections are built under Bear, Base, and Bull cases using the approach commonly used by strategy consulting firms.

2. Data Sources
Primary Dataset
International Energy Agency (IEA) – Global EV Outlook 2024
Includes BEV sales data, historical growth, and regional penetration.
Secondary Validation Sources
Tesla Annual Report (10-K filings)
Statista Global EV Market Data

Raw data is preserved exactly as downloaded for complete transparency.

3. Repository Structure
Market_Sizing/
│
├── 01_Data_Raw/                 
│     └── global_ev_raw.xlsx
│
├── 02_Data_Clean/               
│     └── global_ev_cleaned.xlsx
│
├── 03_Model/                    
│     └── Tesla_MarketSizing_Model.xlsx
│
├── 04_Outputs/                  
│     ├── TAM_SAM_SOM_Charts.png
│     └── Summary_Table.pdf
│
└── README.md
4. Modeling Framework
A. Global BEV Market Projection (TAM)

Using IEA 2020–2024 BEV sales as the baseline, the model applies fixed scenario-based annual growth rates:

Scenario	Growth Rate	Description
Bear	15%	Slower EV adoption
Base	20%	Continuation of current trends
Bull	28%	Accelerated policy & tech adoption

Formula

Market_t = Market_(t-1) × (1 + GrowthRate)
B. Tesla Market Share Projection (SOM)
Scenario	Annual Market Share Change
Bear	–2%
Base	0%
Bull	+2%

Formula

Tesla_Share_t = Tesla_Share_(t-1) + AnnualChange
C. TAM–SAM–SOM Definitions
TAM (Total Addressable Market)
The full global BEV market.
SAM (Serviceable Available Market)
Regions where Tesla currently sells vehicles (North America, Europe, China, selected APAC).
SOM (Serviceable Obtainable Market)
Tesla’s achievable penetration within SAM based on scenario-driven market share projections.

5. Key Outputs
The Excel model automatically generates:

Global BEV market projections (2024–2030)
Tesla unit delivery forecasts
Tesla revenue projections
Market share evolution
Scenario comparisons (Bear/Base/Bull)
TAM–SAM–SOM summaries
Presentation-ready tables and charts

All outputs dynamically update when input assumptions change.

6. How to Use the Model
Open the file:
03_Model/Tesla_MarketSizing_Model.xlsx
Go to the Assumptions sheet.
Modify the following as needed:
BEV growth rates
Tesla starting market share
Chosen scenario (Bear / Base / Bull)
Review updated results in:
Projection tables
Revenue models
Scenario summaries
TAM–SAM–SOM breakdown

Live Interactive Model (Streamlit App)
Experience the full Tesla Market Sizing model here:
➡️ https://marketsizing-9feu2z8zzeyxkhopfemqzq.streamlit.app/

This app includes:

Scenario selection (Bear / Base / Bull)
Interactive BEV market projections
Tesla deliveries forecast
Revenue forecast
TAM–SAM–SOM visualizations


