import pandas as pd
import numpy as np
import scipy
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter

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