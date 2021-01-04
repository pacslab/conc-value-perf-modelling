import itertools

import numpy as np
from .single_model import StateCoder as SingleStateCoder
from . import utility


class StateCoder(SingleStateCoder):
    def __init__(self, config, ):
        self.state_list = StateCoder.generate_state_list(
            config['max_container_count'])

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
        inst_count = int(
            np.ceil(val / config['target_conc'] * config['instance_count']))
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


# calculate probability of transitions to other ready containers
def get_trans_probabilities(ready_count, ordered_count, config):
    if ordered_count == ready_count:
        vals = [ ordered_count ]
        probs = [ 1 ]
    if ordered_count > ready_count:
        possible_state_count = ordered_count - ready_count + 1
        vals = range(ready_count, ordered_count + 1)
        probs = utility.get_trans_probs(possible_state_count, transition_rate_base=config['provision_rate_base'], max_t=config['autoscaling_interval'])
    else:
        possible_state_count = ready_count - ordered_count + 1
        vals = range(ready_count, ordered_count - 1, -1)
        probs = utility.get_trans_probs(possible_state_count, transition_rate_base=config['deprovision_rate_base'], max_t=config['autoscaling_interval'])
    return np.array(vals), np.array(probs)
