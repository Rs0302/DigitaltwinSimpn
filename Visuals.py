import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter
import seaborn as sns
import matplotlib.pyplot as plt
import scipy

import Calculations
from Calculations import inter_arrival_time_out, task_task_transition

directory = "C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv"

data = pd.read_csv(directory)

data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

data_np = data.to_numpy()
#Find case durations

def inter_arrival_boxplot(data):

    data_sorted = data.sort_values("StartTimestamp")
    data_sorted["InterarrivalTime"] = data_sorted["StartTimestamp"].diff().dt.total_seconds()
    sns.histplot(data_sorted["InterarrivalTime"], bins = 30, kde =True)
    plt.xlabel("InterarrivalTime: s")
    plt.show()

    sns.boxplot(data_sorted["InterarrivalTime"])
    plt.ylabel("InterarrivalTime: s")
    plt.show()

    return plt.show()

print(inter_arrival_boxplot(data))

def hist_inter_arrival_out(data):

    clean_data = inter_arrival_time_out(data)

    sns.histplot(clean_data["InterarrivalTime"], bins=30, kde=True)
    plt.title("Interarrival Time Without Outliers (Z_score)")
    plt.xlabel("InterarrivalTime: s")
    plt.show()

    return plt.show()

print(hist_inter_arrival_out(data))


def heat_task_transition(data):

    Next_task_count = task_task_transition(data)

    transition_matrix = Next_task_count.pivot(index="ActivityName", columns="NextActivity", values="Probability")

    sns.heatmap(transition_matrix, annot=True, cmap="coolwarm", linewidths=1)

    plt.xlabel("Next Activity")
    plt.ylabel("Current Activity")
    plt.title("Transition probability between activities")

    plt.show()

    return plt.show()
print(heat_task_transition(data))


def plt_task_resource(data):

    tasks_per_resource = Calculations.task_per_resource(data)

    plt.figure(figsize=(12, 6))
    plt.barh(tasks_per_resource["Resource"], tasks_per_resource["TaskCount"], color="lightblue")
    plt.xlabel("Number of Tasks")
    plt.ylabel("Resource")
    plt.title("Number of Tasks Performed by Each Resource")
    plt.gca().invert_yaxis()  # Invert y-axis for better readability
    plt.show()

    return plt.show()

print(plt_task_resource(data))






