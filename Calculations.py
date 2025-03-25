import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter


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

#The transition time between cases

data_sorted["TransitionTime"] = data_sorted.groupby("CaseId")["StartTimestamp"].diff().dt.total_seconds()

data_sorted = data_sorted.dropna()

avg_transition_time = data_sorted["TransitionTime"].mean()
print(f"Average Transition Time {avg_transition_time:.2f} seconds")

#Find number of resources

n_resource_location = data.groupby(["Location","Role"])["Resource"].nunique().reset_index()

n_resource_location.rename(columns={"Resource":"UniqueRCount"}, inplace = True)

print(n_resource_location)

#Total duration of the process

total_duration = max(data["EndTimestamp"]) - min(data["StartTimestamp"])

print(f'total duration of the dataset is {total_duration}')

#Duration of the Activities

data["TaskDuration"] = (data["EndTimestamp"] - data["StartTimestamp"]).dt.total_seconds()

avg_task_duration = data.groupby("ActivityName")["TaskDuration"].mean().reset_index()

print(f"Average duration per activity: {avg_task_duration}")

#number of each activities

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

#print(f"transition between activities: {Next_task_count}")

transition_matrix = Next_task_count.pivot(index="ActivityName", columns="NextActivity", values="Probability")




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








