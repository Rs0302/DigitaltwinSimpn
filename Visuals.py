import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter
import seaborn as sns
import matplotlib.pyplot as plt

directory = "C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv"

data = pd.read_csv(directory)

#Find case durations

data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

case_durations = data.groupby("CaseId").agg(
    start_time=("StartTimestamp", "min"),
    end_time=("EndTimestamp", "max"))

case_durations["total_duration"] = (case_durations["end_time"] - case_durations["start_time"]).dt.total_seconds()

average_duration = np.mean(case_durations["total_duration"])

print(f"average duration of a case is {average_duration}")

#Find number of unique ID's of tasks

data_np = data.to_numpy()

n_cases = data["CaseId"].nunique()

print(f'Number of cases {n_cases}')

#Find inter arrival time

data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])

data_sorted = data.sort_values("StartTimestamp")

data_sorted["InterarrivalTime"] = data_sorted["StartTimestamp"].diff().dt.total_seconds()

avg_int_time = np.mean(data_sorted["InterarrivalTime"])

print(f'average inter arrival time equals {avg_int_time}')

#Find number of resources

n_resource_location = data.groupby(["Location","Role"])["Resource"].nunique().reset_index()

heatmap_data = n_resource_location.pivot(index="Location", columns = "Role", values = "Resource")

n_resource_location.rename(columns={"Resource":"UniqueRCount"}, inplace = True)

print(n_resource_location)

#Total duration of the process

total_duration = max(data["EndTimestamp"]) - min(data["StartTimestamp"])

print(f'total duration of the dataset is {total_duration}')

#visualization

sns.histplot(data_sorted["InterarrivalTime"], bins = 30, kde =True)
plt.show()

sns.histplot(case_durations["total_duration"], bins = 30, kde =True)
plt.show()

sns.heatmap(heatmap_data, annot=True, cmap="Blues", linewidths=1)
plt.show()

