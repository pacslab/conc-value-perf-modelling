import itertools

import numpy as np
import scipy as sp
from .single_model import StateCoder as SingleStateCoder

class StateCoder(SingleStateCoder):
    def __init__(self, config, ):
        self.state_list = StateCoder.generate_state_list(config['max_container_count'])

    # Generate State List
    @staticmethod
    def generate_state_list(max_conc):
        cont_counts = list(range(max_conc + 1))
        state_list = list(itertools.product(cont_counts, cont_counts, ))
        return state_list

def get_min_max_new_order(config):
    ready_count = config['instance_count']
    min_new_order = int(np.ceil(ready_count / config['max_scale_down_rate']))
    max_new_order = int(np.floor(ready_count * config['max_scale_up_rate']))
    # we can add at least 1 container
    max_new_order = max(max_new_order, ready_count + 1)
    max_new_order = min(max_new_order, config['max_container_count'])
    # no scale down in panic mode
    # if status == 'p':
    #     min_new_order = ready_count

    return min_new_order, max_new_order

def get_new_order_dist(req_count_averaged_vals, req_count_averaged_probs, config):
    min_new_order, max_new_order = get_min_max_new_order(config)
    dist_ordered_inst = {i: 0 for i in range(config['max_container_count']+1)}
    for val, prob in zip(req_count_averaged_vals, req_count_averaged_probs):
        inst_count = int(np.ceil(val / config['target_conc'] * config['instance_count']))
        # if less than lower threshold, sum up at threshold
        if inst_count < min_new_order:
            dist_ordered_inst[min_new_order] += prob
        # if more than upper threshold, sum up at threshold
        elif inst_count > max_new_order:
            dist_ordered_inst[max_new_order] += prob
        # if between thresholds, regular addition would be fine
        else:
            dist_ordered_inst[inst_count] += prob

    return np.array(list(dist_ordered_inst.keys())), np.array(list(dist_ordered_inst.values()))


def get_prov_trans_probs(ready_count, next_ready_counts, provision_rate_base, deprovision_rate_base, max_t=2):
    state_count = len(next_ready_counts)
    next_ready_counts = np.array(next_ready_counts)

    ready_idx = np.where(next_ready_counts==ready_count)
    if len(ready_idx) == 0:
        raise ValueError('ready_count not found in next_ready_counts')
    ready_idx = ready_idx[0][0]

    Q = np.zeros((state_count, state_count))
    # our initial state
    init_state = np.zeros(state_count)
    init_state[ready_idx] = 1

    # the first one and last one cannot be source states (they are absorbing)
    for i, next_ready_count in enumerate(next_ready_counts):
        if i == 0 or i == next_ready_counts[-1]:
            continue

        rate = np.abs(next_ready_count - ready_count)
        if ready_count <= next_ready_count:
            rate *= provision_rate_base
            Q[i, i+1] = rate
        else:
            rate *= deprovision_rate_base
            Q[i, i-1] = rate

        Q[i,i] = -1 * rate

    solution = init_state @ sp.linalg.expm(Q * max_t)
    return solution, Q

