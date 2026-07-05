"""
Synthetic test fixture: survival analysis of a treatment on time-to-event.
Mock cohort. For auditor evaluation only.
"""
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

df = pd.read_csv("/Users/lab/data/cohort_final_v3.csv")

# Define the treatment group
df["treated"] = df["drug_start_day"].notna().astype(int)

cph = CoxPHFitter()
cph.fit(df[["time", "event", "treated", "age"]],
        duration_col="time", event_col="event")

hr = np.exp(cph.params_["treated"])
print(f"Hazard ratio for treatment: {hr:.2f}")
