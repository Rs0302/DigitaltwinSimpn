import pandas as pd
import numpy as np
import scipy
from simpn.prototypes import BPMNTask, BPMNStartEvent
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter
from simpn.visualisation import Visualisation
import json
import Calculations
from Calculations import task_duration_resource, duration_lookup, resource_task_map, task_task_transition, \
    inter_arrival_time
import math

directory = "C:/Users/20213010/OneDrive - TU Eindhoven/Documents/TBK/BEP/SampleData.csv"

data = pd.read_csv(directory)

sim = SimProblem()

#Task operators
inv_pros = sim.add_var("Invoice Processor")
inv_app = sim.add_var("Invoice Approver")


#Queues
inv_req = sim.add_var("Invoice Request")
app_req = sim.add_var("Approval Request")
req_check_pay = sim.add_var("Queue Check Customer Payment")
req_comp_cust_memo = sim.add_var("Queue Complete the Customer Memo")
req_conf_pay_recv = sim.add_var("Queue Confirm Payment Received")
req_cred_memo_create = sim.add_var("Queue Credit Memo Creation")
req_cred_memo_entry = sim.add_var("Queue Credit Memo Entry")
req_fill_cred_memo = sim.add_var("Queue Fill Credit Memo")
req_refund_cust = sim.add_var("Queue Refund Customer")
req_refund_spec_voucher = sim.add_var("Queue Refund With Special Voucher")
req_refund_std_voucher = sim.add_var("Queue Refund With Standard Voucher")
req_reject_inv = sim.add_var("Queue Reject Invoice")
req_reissue_inv = sim.add_var("Queue Re-issuing the Invoice")

#Choices
c_comp_cust = sim.add_var("Choose between rejecting or approving after Completing Customer Memo")
c_conf_pay = sim.add_var("Choose between refunding with special or standard voucher after confirming payment received")
c_inv_entry = sim.add_var("Choose between check customer payment or confirm payment received after invoice entry")
c_rej_inv = sim.add_var("Choose between refund with special or standard voucher after rejecting the invoice")

#resources
inv_app.put("Jessie")
inv_app.put("Jackie")
inv_app.put("Addison")

inv_pros.put("Casey")
inv_pros.put("Abbie")
inv_pros.put("Adrian")
inv_pros.put("Aiden")
inv_pros.put("Riley")

#finish
done = sim.add_var("done")

with open("res_task_json.json", "r") as f:
    lookup_dict = json.load(f)

def working_hours(c,r):
    time = sim.clock
    hour = (time / 3600) % 24
    day = (time / 86400) % 7


    return (0 <= day <= 4) and (9 <= hour <= 17)

def resource_task_behavior(resource_name, task_name, lookup_dict):
    try:
        stats = lookup_dict[resource_name][task_name]
        mean = stats["mean"]
        std = stats["std"]

        delay = max(1, np.random.normal(loc=mean, scale=std))
        return delay
    except KeyError:
        # Default delay if missing
        return 10000

#delay = np.random.lognormal(1000, 800)

from simpn.reporters import Reporter


class MyReporter(Reporter):
    def __init__(self):
        self.logs = []
        self.case_start_times = {}
        self.case_end_times = {}

    def callback(self, timed_binding):

        binding, time, event = timed_binding

        day = int(time) / 86400
        seconds = int(time) % 86400

        day_int = math.ceil(day)

        timestamp = f"Day {day_int}, Second {seconds:05}"

        event_name = getattr(event, "name", str(event))
        bound_values = ", ".join(str(v) for v in binding)

        log_line = f"[{timestamp}] Fired: {event_name} with value: {bound_values}"
        print(log_line)
        self.logs.append(log_line)

        for _ in binding:
            if isinstance(_, tuple) and isinstance(_[0], str):
                case_id = _[0]
            elif isinstance(_, str):
                case_id = _
            else:
                continue

            if "arrival" in event_name.lower():
                self.case_start_times[case_id] = time
            elif "approved" in event_name.lower() or "done" in event_name.lower():
                self.case_end_times[case_id] = time

    def get_average_case_time(self):
        total_time = 0
        count = 0
        for case_id in self.case_start_times:
            if case_id in self.case_end_times:
                duration = self.case_end_times[case_id] - self.case_start_times[case_id]
                total_time += duration
                count += 1
        return total_time / count if count > 0 else 0

    def get_logs(self):
        return self.logs

def inv_entry(c, r):
    task_name = "Invoice Entry"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return[SimToken((c, r), delay = delay)]
BPMNTask(sim, [inv_req, inv_pros], [c_inv_entry, inv_pros], "Invoice Entry", inv_entry, guard=working_hours)

def check_cust_pay(c, r):
    task_name = "Check Customer Payment"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return[SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_check_pay, inv_pros], [req_cred_memo_entry, inv_pros], "Check Customer Payment", check_cust_pay, guard=working_hours)

def conf_pay_rec(c, r):
    task_name = "Confirm Payment Received"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return[SimToken((c,r), delay = delay)]
BPMNTask(sim, [req_conf_pay_recv, inv_pros], [c_conf_pay, inv_pros], "Confirm Payment Received", conf_pay_rec, guard=working_hours)

def cred_memo_ent(c, r):
    task_name = "Credit Memo Entry"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return[SimToken((c,r), delay = delay)]
BPMNTask(sim, [req_cred_memo_entry, inv_pros], [req_refund_cust, inv_pros], "Credit Memo Entry", cred_memo_ent, guard=working_hours)

def cred_memo_create(c,r):
    task_name = "Credit Memo Creation"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return[SimToken((c,r), delay = delay)]
BPMNTask(sim, [req_cred_memo_create, inv_pros], [req_fill_cred_memo, inv_pros], "Credit Memo Creation", cred_memo_create, guard=working_hours)

def fill_cred_memo(c,r):
    task_name = "Fill Credit Memo"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_fill_cred_memo, inv_pros], [req_reissue_inv, inv_pros], "Fill Credit Memo", fill_cred_memo, guard=working_hours)

def ref_cust(c, r):
    task_name = "Refund Customer"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_refund_cust, inv_pros], [req_reissue_inv, inv_pros], "Refund Customer", ref_cust, guard=working_hours)

def reissue_inv(c, r):
    task_name = "Re-issuing the invoice"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_reissue_inv, inv_pros], [done, inv_pros], "Re-Issuing the Invoice", reissue_inv, guard=working_hours)

def ref_special(c, r):
    task_name = "Refund With Special Voucher"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return[SimToken((c,r), delay = delay)]
BPMNTask(sim, [req_refund_spec_voucher, inv_pros], [req_comp_cust_memo, inv_pros], "Refund with Special Voucher", ref_special, guard=working_hours)

def ref_standard(c, r):
    task_name = "Refund With Standard Voucher"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_refund_std_voucher, inv_pros], [req_comp_cust_memo, inv_pros], "Refund with Standard Voucher", ref_standard, guard=working_hours)

def comp_cust_memo(c, r):
    task_name = "Complete the Customer Memo"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_comp_cust_memo, inv_app], [c_comp_cust, inv_app], "Complete the Customer Memo", comp_cust_memo, guard=working_hours)

def rej_inv (c,r):
    task_name = "Reject Invoice"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [req_reject_inv, inv_app], [c_rej_inv, inv_app], "Reject Invoice", rej_inv, guard=working_hours)

def approve(c, r):
    task_name = "Approve Invoice"
    resource_name = r
    delay = resource_task_behavior(resource_name, task_name, lookup_dict)
    return [SimToken((c, r), delay = delay)]
BPMNTask(sim, [app_req, inv_app], [done, inv_app], "approved", approve, guard=working_hours)

def interarrival_time():
    return 26659
BPMNStartEvent(sim, [], [inv_req], "arrival", interarrival_time)

def c_comp_cust_memo(c):
    percentage = np.random.uniform(1,1000)
    if percentage <= 575:
        return [SimToken(c), None]
    else:
        return [None, SimToken(c)]
sim.add_event([c_comp_cust], [app_req, req_reject_inv], c_comp_cust_memo)

def c_conf_pay_rec(c):
    percentage = np.random.uniform(1,1000)
    if percentage <= 138:
        return [SimToken(c), None]
    else:
        return [None, SimToken(c)]
sim.add_event([c_conf_pay], [req_refund_spec_voucher, req_refund_std_voucher], c_conf_pay_rec)

def c_invoice_entry(c):
    percentage = np.random.uniform(1,1000)
    if percentage <= 511:
        return [SimToken(c), None]
    else:
        return [None, SimToken(c)]
sim.add_event([c_inv_entry], [req_check_pay, req_conf_pay_recv], c_invoice_entry)

def c_reject_inv(c):
    percentage = np.random.uniform(1, 1000)
    if percentage <= 62:
        return [SimToken(c), None]
    else:
        return [None, SimToken(c)]
sim.add_event([c_rej_inv], [req_refund_spec_voucher, req_refund_std_voucher], c_reject_inv)


#v = Visualisation(sim)
#v.show()

reporter = MyReporter()

sim.simulate(3628800, MyReporter())

avg_case_time = reporter.get_average_case_time()
print(f"average case time equals {avg_case_time}")







