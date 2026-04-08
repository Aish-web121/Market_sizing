import pandas as pd

df = pd.read_excel("EV Data Explorer 2025.xlsx", engine="openpyxl")

result = df[
    (df["region_country"] == "World") &
    (df["powertrain"] == "BEV") &
    (df["parameter"] == "EV sales") &
    (df["category"] == "Historical")
][["year", "value", "category", "mode"]].sort_values("year")

print(result.to_string())