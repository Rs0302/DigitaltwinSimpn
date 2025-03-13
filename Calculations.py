import pandas as pd
import numpy as np
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter

directory = "C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv"

data =pd.read_csv(directory)

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

n_resource_location.rename(columns={"Resource":"UniqueRCount"}, inplace = True)

print(n_resource_location)

#Total duration of the process

total_duration = max(data["EndTimestamp"]) - min(data["StartTimestamp"])

print(f'total duration of the dataset is {total_duration}')

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








