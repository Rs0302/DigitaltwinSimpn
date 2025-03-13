import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
import pm4py
import graphviz

directory = "C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv"

df = pd.read_csv(directory)
nan_values = df.isnull().any().any()

''''
log = pm4py.read.read_ocel_csv("C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv")
process_model = pm4py.discover_bpmn_inductive(log)
pm4py.view_bpmn(process_model)

print(df)
'''


# Display the first few rows
print(df.head())

# Check for missing values
print("\nMissing values per column:\n", df.isnull().sum())

# Define column mapping for event log conversion
event_log = pm4py.format_dataframe(
    df,
    case_id="CaseId",  # Adjust based on your file
    activity_key="ActivityName",  # Adjust based on your file
    timestamp_key="StartTimestamp"  # Adjust based on your file
)

# Convert to event log format
log = pm4py.convert_to_event_log(event_log)

# Check log summary
print(log)

# Discover a BPMN process model
process_model = pm4py.discover_bpmn_inductive(log)

# Visualize the process model
pm4py.view_bpmn(process_model)

