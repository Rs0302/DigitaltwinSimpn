import pandas as pd
import numpy as np
import scipy
import json



directory = "C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv"

data = pd.read_csv(directory)

#Find case durations

def case_duration(data):

    data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
    data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

    case_durations = data.groupby("CaseId").agg(
        start_time=("StartTimestamp", "min"),
        end_time=("EndTimestamp", "max"))

    case_durations["total_duration"] = (case_durations["end_time"] - case_durations["start_time"]).dt.total_seconds()

    average_duration = np.mean(case_durations["total_duration"])

    return average_duration

print(f"average duration of a case is {case_duration(data)}")

#Find number of unique ID's of tasks

def n_cases(data):

    data_np = data.to_numpy()

    n_cases = data["CaseId"].nunique()

    return n_cases

print(f'Number of cases {n_cases(data)}')

#Find inter arrival time

def inter_arrival_time(data):

    data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])

    data_sorted = data.sort_values("StartTimestamp")

    data_sorted["InterarrivalTime"] = data_sorted["StartTimestamp"].diff().dt.total_seconds()

    avg_int_time = np.mean(data_sorted["InterarrivalTime"])

    return avg_int_time

print(f'average inter arrival time equals {inter_arrival_time(data)}')

def inter_arrival_time_out(data):

    data_sorted = data.sort_values("StartTimestamp")

    data["StartTimestamp"] = pd.to_datetime(data_sorted["StartTimestamp"])

    data_sorted["InterarrivalTime"] = data_sorted["StartTimestamp"].diff().dt.total_seconds()

    data_sorted["Z_score"] = scipy.stats.zscore(data_sorted["InterarrivalTime"], nan_policy = "omit")

    threshold_Z = 2

    no_outliers_z = data_sorted[(data_sorted["Z_score"] < threshold_Z)]

    #output = no_outliers_z["InterarrivalTime"].mean()

    return no_outliers_z


#The transition time between cases

def transition_time_cases(data):

    data_sorted = data.sort_values("StartTimestamp")

    data_sorted["TransitionTime"] = data_sorted.groupby("CaseId")["StartTimestamp"].diff().dt.total_seconds()

    data_sorted = data_sorted.dropna()

    avg_transition_time = data_sorted["TransitionTime"].mean()

    return avg_transition_time

print(f"Average Transition Time {transition_time_cases(data)} seconds")


#Find number of resources per location

def resource_location(data):

    n_resource_location = data.groupby(["Location","Role"])["Resource"].nunique().reset_index()

    n_resource_location.rename(columns={"Resource":"UniqueRCount"}, inplace = True)

    return n_resource_location

print(f"resource per location: {resource_location(data)}")

#Total duration of the process

def total_duration(data):

    total_duration = max(data["EndTimestamp"]) - min(data["StartTimestamp"])

    return total_duration
print(f'total duration of the dataset is {total_duration(data)}')

#Duration of the Activities

def avg_task_duration(data):

    data["TaskDuration"] = (data["EndTimestamp"] - data["StartTimestamp"]).dt.total_seconds()

    avg_task_duration = data.groupby("ActivityName")["TaskDuration"].mean().reset_index()

    return avg_task_duration

print(f"Average duration per activity: {avg_task_duration(data)}")

#number of each activities

def number_activities(data):

    N_of_activity = data["ActivityName"].value_counts()

    return N_of_activity

print(f"Number of different activities {number_activities(data)}")

#Probability of a task being in a case

def p_task_in_case(data):

    P_task = number_activities(data)/n_cases(data)

    return P_task

print(f"Probability of a task being in a case {p_task_in_case(data)}")

#Probability of next task being a certain task

def task_task_transition(data):

    data_sorted_CaseID = data.sort_values(by=["CaseId", "StartTimestamp"])

    data_sorted_CaseID["NextActivity"] = data_sorted_CaseID.groupby("CaseId")["ActivityName"].shift(-1)

    Next_task = data_sorted_CaseID.dropna(subset=["NextActivity"]) # drop when no next task (new case)

    Next_task_count = Next_task.groupby(["ActivityName", "NextActivity"]).size().reset_index(name="Count")

    Next_task_count["TotalCount"] = Next_task_count.groupby("ActivityName")["Count"].transform("sum")

    Next_task_count["Probability"] = Next_task_count["Count"] / Next_task_count["TotalCount"]

    Next_task_count.drop(columns=["TotalCount"], inplace=True)

    return Next_task_count

#print(f"transition between activities: {task_task_transition(data)}")

transition_matrix = task_task_transition(data).pivot(index="ActivityName", columns="NextActivity", values="Probability")

#Duration of each task

def task_duration(data):

    data["TaskDuration"] = (data["EndTimestamp"] - data["StartTimestamp"]).dt.total_seconds()

    avg_task_duration = data.groupby("ActivityName")["TaskDuration"].mean().reset_index()

    task_std = data.groupby("ActivityName")["TaskDuration"].std().reset_index()

    avg_task_duration.columns = ["ActivityName", "AvgTaskDuration"]

    task_std.columns = ["ActivityName", "Std_TaskDuration"]

    task_stats = avg_task_duration.merge(task_std, on = "ActivityName", how = "left")

    return task_stats

print(task_duration(data))

# Rename for clarity

print(avg_task_duration)

#average task per resource

def task_per_resource(data):

    tasks_per_resource = data.groupby("Resource")["ActivityName"].count().reset_index()

    tasks_per_resource.columns = ["Resource", "TaskCount"]

    return tasks_per_resource

# Rename for clarity


print(task_per_resource(data))

def task_duration_resource(data):
    data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
    data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

    data["TaskDuration"] = (data["EndTimestamp"] - data["StartTimestamp"]).dt.total_seconds()

    avg_task_duration = data.groupby(["Resource", "ActivityName"])["TaskDuration"].mean().reset_index()

    task_std = data.groupby(["Resource", "ActivityName"])["TaskDuration"].std().reset_index()

    avg_task_duration.rename(columns={"TaskDuration": "AverageDurationSeconds"}, inplace=True)
    task_std.rename(columns={"TaskDuration": "StdTaskDuration"}, inplace=True)

    task_resource_stats = avg_task_duration.merge(task_std, on = ["Resource", "ActivityName"], how = "left")

    return task_resource_stats

print(task_duration_resource(data))

def resource_calendar(data):
    # Convert timestamps to datetime
    data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
    data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

    # Sort data by Resource and StartTimestamp
    data = data.sort_values(by=["Resource", "StartTimestamp"])

    # Calculate availability (gaps between tasks)
    data["NextStart"] = data.groupby("Resource")["StartTimestamp"].shift(-1)
    data["Availability"] = (data["NextStart"] - data["EndTimestamp"]).dt.total_seconds()

    # Remove negative or NaN values (end of dataset cases)
    availability_df = data[["Resource", "EndTimestamp", "NextStart", "Availability"]].dropna()
    availability_df = availability_df[availability_df["Availability"] > 0]

    # Calculate daily, monthly, and yearly availability
    availability_df["Date"] = availability_df["EndTimestamp"].dt.date
    availability_df["Month"] = availability_df["EndTimestamp"].dt.to_period("M")
    availability_df["Year"] = availability_df["EndTimestamp"].dt.year

    avg_daily = availability_df.groupby(["Resource", "Date"])["Availability"].sum().reset_index()
    avg_monthly = availability_df.groupby(["Resource", "Month"])["Availability"].sum().reset_index()
    avg_yearly = availability_df.groupby(["Resource", "Year"])["Availability"].sum().reset_index()

    return availability_df, avg_daily, avg_monthly, avg_yearly

print(resource_calendar(data))

def resource_task_map(data):
    return data.groupby("Resource")["ActivityName"].unique().to_dict()

def duration_lookup(data):
    stats = task_duration_resource(data)
    duration_lookup = {}

    for _, row in stats.iterrows():
        duration_lookup[(row["Resource"], row["ActivityName"])] = {
            "mean": row["AverageDurationSeconds"],
            "std": row["StdTaskDuration"]
        }

    return duration_lookup

print(inter_arrival_time_out(data))


def resource_task_statistics(data):

    data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
    data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

    data["TaskDuration"] = (data["EndTimestamp"] - data["StartTimestamp"]).dt.total_seconds()

    stats = data.groupby(["Resource", "ActivityName"])["TaskDuration"].agg(["mean", "std"]).reset_index()

    stats = stats.rename(columns={"mean": "MeanDuration", "std": "StdDuration"})

    return stats


def res_task_json(data):
    stats_df = resource_task_statistics(data)

    lookup = {}
    for _, row in stats_df.iterrows():
        resource = row["Resource"]
        activity = row["ActivityName"]
        mean = row["MeanDuration"]
        std = row["StdDuration"]

        if resource not in lookup:
            lookup[resource] = {}

        lookup[resource][activity] = {
            "mean": mean,
            "std": std
        }

    lookup_json = json.dumps(lookup, indent = 4)

    return lookup, lookup_json

lookup_dict, lookup_json = res_task_json(data)

with open("res_task_json.json", "w") as f:
    json.dump(lookup_dict, f, indent = 4)

print(res_task_json(data))



