import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter
import seaborn as sns
import matplotlib.pyplot as plt
import scipy

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

sns.boxplot(data_sorted["InterarrivalTime"])
plt.show()

#remove outliers with Z score

data_sorted["Zscore"] = scipy.stats.zscore(data_sorted["InterarrivalTime"], nan_policy = "omit")

threshold_Z = 2

no_outliers_z = data_sorted[(data_sorted["Zscore"] < threshold_Z)]

print("Original dataset shape:", data_sorted.shape)
print("Dataset without outliers (Z-score method):", no_outliers_z.shape)

sns.boxplot(no_outliers_z["InterarrivalTime"])
plt.title("Interarrival Time Without Outliers (Z-score)")
plt.show()

sns.histplot(no_outliers_z["InterarrivalTime"], bins=30, kde=True)
plt.title("Interarrival Time Without Outliers (Z-score)")
plt.show()

sns.histplot(case_durations["total_duration"], bins = 30, kde =True)
plt.show()

sns.heatmap(heatmap_data, annot=True, cmap="Blues", linewidths=1)
plt.show()

#Number of total different activities

N_of_activity = data["ActivityName"].value_counts()

print(f"Number of different activities {N_of_activity}")

#Probability of a case being in a case

P_task = N_of_activity/n_cases

print(f"Probability of a task being in a case {P_task}")

#Probability of next task being a certain task

data_sorted_CaseID = data.sort_values(by=["CaseId", "StartTimestamp"])

data_sorted_CaseID["NextActivity"] = data_sorted_CaseID.groupby("CaseId")["ActivityName"].shift(-1)

Next_task = data_sorted_CaseID.dropna(subset=["NextActivity"]) # drop when no next task (new case)

Next_task_count = Next_task.groupby(["ActivityName", "NextActivity"]).size().reset_index(name="Count")

Next_task_count["TotalCount"] = Next_task_count.groupby("ActivityName")["Count"].transform("sum")

Next_task_count["Probability"] = Next_task_count["Count"] / Next_task_count["TotalCount"]

Next_task_count.drop(columns=["TotalCount"], inplace=True)

transition_matrix = Next_task_count.pivot(index="ActivityName", columns="NextActivity", values="Probability")

sns.heatmap(transition_matrix, annot=True, cmap="coolwarm")

plt.xlabel("Next Activity")
plt.ylabel("Current Activity")
plt.title("Transition probability between activities")

plt.show()



