import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter

#from Visuals import average_duration

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

    return avg_task_duration

# Rename for clarity
avg_task_duration.columns = ["ActivityName", "AvgTaskDuration"]

print(avg_task_duration)

#average task per resource

def task_per_resource(data):

    tasks_per_resource = data.groupby("Resource")["ActivityName"].count().reset_index()

    return tasks_per_resource

# Rename for clarity
task_per_resource(data).columns = ["Resource", "TaskCount"]

print(task_per_resource)

def task_duration_resource(data):
    data["StartTimestamp"] = pd.to_datetime(data["StartTimestamp"])
    data["EndTimestamp"] = pd.to_datetime(data["EndTimestamp"])

    # Calculate task duration
    data["TaskDuration"] = (data["EndTimestamp"] - data["StartTimestamp"]).dt.total_seconds()

    # Group by Resource and ActivityName to compute the average duration
    avg_task_duration = data.groupby(["Resource", "ActivityName"])["TaskDuration"].mean().reset_index()

    # Rename column for clarity
    avg_task_duration.rename(columns={"TaskDuration": "AverageDurationSeconds"}, inplace=True)

    return avg_task_duration
task_durations = task_duration_resource(data)
print(task_durations)

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


''''

#Simulate process


# Create a simulation model
process_sim = SimProblem()

# Define process state variables
arrival = process_sim.add_var("arrival")
waiting = process_sim.add_var("waiting")
resource = process_sim.add_var("resource")
busy = process_sim.add_var("busy")

# Initialize simulation state
resource.put("R1")
resource.put("R2")
resource.put("R3")
resource.put("R4")
resource.put("R5")
#resource.put("R6")
#resource.put("R7")

arrival.put(1)  # Start case numbering

# Define event: case arrival with interarrival time from the dataset

def arrive(a):
    return [SimToken(a+1, delay=3716), SimToken(f"Case_{a}")]

process_sim.add_event([arrival], [arrival, waiting], arrive)

# Define event: start processing a case, with delay of the time from the dataset
def start(c, r):
    return [SimToken((c, r), delay=206276)]  # Exponential service time

process_sim.add_event([waiting, resource], [busy], start)

# Define event: complete processing
def complete(b):
    return [SimToken(b[1])]  # Resource becomes available again

process_sim.add_event([busy], [resource], complete)

# Run the simulation for the time from the datasets
process_sim.simulate(3730956, SimpleReporter())

#changes 2
'''








