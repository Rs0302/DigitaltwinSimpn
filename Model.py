import pandas as pd
import numpy as np
import scipy
from simpn.prototypes import BPMNTask, BPMNStartEvent
from simpn.simulator import SimProblem, SimToken
from simpn.reporters import SimpleReporter
import Calculations
from Calculations import task_duration_resource, duration_lookup, resource_task_map, task_task_transition, \
    inter_arrival_time

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

def inv_entry(c, r):
    return[SimToken((c, r), delay = np.random.normal(10843, 9366))]
BPMNTask(sim, [inv_req, inv_pros], [c_inv_entry, inv_pros], "Invoice Entry", inv_entry)

def check_cust_pay(c, r):
    return[SimToken((c, r), delay = np.random.normal(9889, 9259))]
BPMNTask(sim, [req_check_pay, inv_pros], [req_cred_memo_entry, inv_pros], "Check Customer Payment", check_cust_pay)

def conf_pay_rec(c, r):
    return[SimToken((c,r), delay = np.random.normal(10731, 8874))]
BPMNTask(sim, [req_conf_pay_recv, inv_pros], [c_conf_pay, inv_pros], "Confirm Payment Received", conf_pay_rec)

def cred_memo_ent(c, r):
    return[SimToken((c,r), delay = np.random.normal(9450, 9106))]
BPMNTask(sim, [req_cred_memo_entry, inv_pros], [req_refund_cust, inv_pros], "Credit Memo Entry", cred_memo_ent)

def cred_memo_create(c,r):
    return[SimToken((c,r), delay = np.random.normal(9073, 9260))]
BPMNTask(sim, [req_cred_memo_create, inv_pros], [req_fill_cred_memo, inv_pros], "Credit Memo Creation", cred_memo_create)

def fill_cred_memo(c,r):
    return [SimToken((c, r), delay = np.random.normal(8374, 8562))]
BPMNTask(sim, [req_fill_cred_memo, inv_pros], [req_reissue_inv, inv_pros], "Fill Credit Memo", fill_cred_memo)

def ref_cust(c, r):
    return [SimToken((c, r), delay = np.random.normal(10750, 8897))]
BPMNTask(sim, [req_refund_cust, inv_pros], [req_reissue_inv, inv_pros], "Refund Customer", ref_cust)

def reissue_inv(c, r):
    return [SimToken((c, r), delay = np.random.normal(8122, 8952))]
BPMNTask(sim, [req_reissue_inv, inv_pros], [done, inv_pros], "Re-Issuing the Invoice", reissue_inv)

def ref_special(c, r):
    return[SimToken((c,r), delay = np.random.normal(53918, 14874))]
BPMNTask(sim, [req_refund_spec_voucher, inv_pros], [req_comp_cust_memo, inv_pros], "Refund with Special Voucher", ref_special)

def ref_standard(c, r):
    return [SimToken((c, r), delay = np.random.normal(5652, 5907))]
BPMNTask(sim, [req_refund_std_voucher, inv_pros], [req_comp_cust_memo, inv_pros], "Refund with Standard Voucher", ref_standard)

def comp_cust_memo(c, r):
    return [SimToken((c, r), delay = np.random.normal(15756, 8254))]
BPMNTask(sim, [req_comp_cust_memo, inv_app], [c_comp_cust, inv_app], "Complete the Customer Memo", comp_cust_memo)

def rej_inv (c,r):
    return [SimToken((c, r), delay = np.random.normal(12428, 6778))]
BPMNTask(sim, [req_reject_inv, inv_app], [c_rej_inv, inv_app], "Reject Invoice", rej_inv)

def approve(c, r):
    shape = 0.9208966428068127
    loc = 0
    scale = 6496.16170284509
    delay = scipy.stats.lognorm.rvs(shape, loc=loc, scale = scale)
    return [SimToken((c, r), delay = np.random.normal(172627, 9045))]
BPMNTask(sim, [app_req, inv_app], [done, inv_app], "approved", approve)

def interarrival_time():
    return 3716
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

sim.simulate(1000000, SimpleReporter())






