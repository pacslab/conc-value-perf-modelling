import itertools

import numpy as np
import scipy.stats as stats
from tqdm.auto import tqdm

from .single_model import StateCoder as SingleStateCoder
from . import utility
from . import single_model


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
    min_new_order = int(np.floor(ready_count / config['max_scale_down_rate']))
    max_new_order = int(np.ceil(ready_count * config['max_scale_up_rate']))
    # we can add at least 1 container
    max_new_order = max(max_new_order, ready_count + 1)
    max_new_order = min(max_new_order, config['max_container_count'])
    # we can deduct at least 1 container
    min_new_order = min(min_new_order, ready_count - 1)
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

def solve_general_model(model_config, update_config, debug=False, show_progress=False):

    # create state coders
    single_coder = single_model.StateCoder(config=model_config)
    general_state_coder = StateCoder(model_config)

    if debug:
        print('Number of states:', general_state_coder.get_state_count())

    state_count = general_state_coder.get_state_count()
    general_P = np.zeros((state_count, state_count))
    inst_count_possible_values = list(range(0, model_config['max_container_count']+1))
    inst_count_possible_values = np.array(inst_count_possible_values)
    all_req_count_prob = []
    req_count_value = np.array([s[0] for s in single_coder.get_state_list()])
    
    if show_progress:
        iterable_inst_count_possible_values = tqdm(inst_count_possible_values, position=0)
    else:
        iterable_inst_count_possible_values = inst_count_possible_values
    for ready_inst_count in iterable_inst_count_possible_values:
        # add instance count to config
        model_config.update({
            'instance_count': max(ready_inst_count, 1), # for 0 ready containers, solve CC with single server
        })

        # update the config
        update_config(model_config)

        # calculate and show Q (no longer used)
        # single_Q = single_model.get_single_container_q(single_coder, config=model_config)
        # display(pd.DataFrame(single_Q))
        # req_count_prob = utility.solve_CTMC(single_Q)
        coeffs2 = model_config['conc_average_model']
        lambda_over_n = model_config['arrival_rate_total'] / np.clip(ready_inst_count, a_min=1, a_max=np.inf)
        normal_mean = (lambda_over_n ** 2) * coeffs2[2] + lambda_over_n * coeffs2[1] + coeffs2[0]
        normal_std = normal_mean * 0.07

        # since we won't be summing up, we need more granular req count values
        req_count_value = np.linspace(0, model_config['max_conc'], 100)

        req_count_prob = stats.norm.pdf(req_count_value, loc=normal_mean, scale=normal_std)
        req_count_prob = req_count_prob / req_count_prob.sum()

        all_req_count_prob.append(req_count_prob)

        # if 0 instances, any value for request count over 0 causes transition to 1 instances
        if ready_inst_count == 0:
            new_order_vals = [0, 1]
            new_order_probs_zero = req_count_prob[req_count_value == 0][0]
            new_order_probs_one = 1 - new_order_probs_zero
            new_order_probs = [new_order_probs_zero, new_order_probs_one]
        else:
            # calculate measure concurrency distribution
            avg_count = model_config['stable_conc_avg_count']
            import time
            start_time = time.time()

            req_count_averaged_vals = req_count_value
            req_count_averaged_probs = req_count_prob

            if debug:
                print(f"new order calculation took {time.time() - start_time} seconds for {ready_inst_count} instances")

            # calculate probability of different ordered instance count
            new_order_vals, new_order_probs = get_new_order_dist(req_count_averaged_vals, req_count_averaged_probs, model_config)

        # now calculate probs according to number of ordered instances
        for ordered_inst_count in inst_count_possible_values:
            # get idx of the "from" state
            from_state_idx = general_state_coder.to_idx(state=(ordered_inst_count, ready_inst_count))

            # calculate probability of number of ready instances
            next_ready_vals, next_ready_probs = get_trans_probabilities(ready_count=ready_inst_count, ordered_count=ordered_inst_count, config=model_config)

            # convert to numpy
            new_order_vals = np.array(new_order_vals)
            new_order_probs = np.array(new_order_probs)
            next_ready_vals = np.array(next_ready_vals)
            next_ready_probs = np.array(next_ready_probs)

            # filter unlikely states
            PROB_THRESHOLD = 1e-3
            new_order_filtered_idxs = np.where(new_order_probs > PROB_THRESHOLD)
            next_ready_filtered_idxs = np.where(next_ready_probs > PROB_THRESHOLD)

            new_order_vals = new_order_vals[new_order_filtered_idxs]
            new_order_probs = new_order_probs[new_order_filtered_idxs]
            next_ready_vals = next_ready_vals[next_ready_filtered_idxs]
            next_ready_probs = next_ready_probs[next_ready_filtered_idxs]

            # faster probability calculations
            if len(new_order_vals) > 0:
                for next_ready_idx in range(len(next_ready_vals)):
                    next_ready_val = next_ready_vals[next_ready_idx]
                    next_ready_prob = next_ready_probs[next_ready_idx]
                    
                    to_state_idxs = np.array([general_state_coder.to_idx(state=(new_order_val, next_ready_val)) for new_order_val in new_order_vals])
                    general_P[from_state_idx, to_state_idxs] = new_order_probs * next_ready_prob

    if debug:
        # when everything is fixed, this should all be ones (almost, because of rounding errors)
        print('values in P that are far from 1 (threshold of 1e-6): ', np.where((general_P.sum(axis=1)-1) > 1e-6))
        # we don't want to be stuck in a specific state
        print('index of values in P that are equal to 1 (stuck forever): ', np.where(general_P == 1))

    inst_count_probs = utility.solve_DTMC(general_P)
    ready_probs = inst_count_probs.reshape((len(inst_count_possible_values),-1)).sum(axis=0)
    ordered_probs = inst_count_probs.reshape((len(inst_count_possible_values),-1)).sum(axis=1)

    return {
        'inst_count_possible_values': inst_count_possible_values,
        'inst_count_probs': inst_count_probs,
        'ready_probs': ready_probs,
        'ordered_probs': ordered_probs,
        'req_count_probs': np.array(all_req_count_prob),
        'req_count_values': req_count_value,
    }


def calculate_general_params(res, model_config, debug=False):
    ready_avg = (res['inst_count_possible_values'] * res['ready_probs']).sum()
    ordered_avg = (res['inst_count_possible_values'] * res['ordered_probs']).sum()

    req_count_probs_weighted = res['req_count_probs'].T @ res['ready_probs']
    req_count_avg = (res['req_count_values'] * req_count_probs_weighted).sum()

    lambda_over_n = model_config['arrival_rate_total'] / np.clip(res['inst_count_possible_values'], a_min=1, a_max=np.inf)
    coeffs2 = model_config['resp_time_model']
    resp_time_values = (lambda_over_n ** 2) * coeffs2[2] + lambda_over_n * coeffs2[1] + coeffs2[0]
    resp_time_avg = (resp_time_values * res['ready_probs']).sum()

    return {
        'ready_avg': ready_avg,
        'ordered_avg': ordered_avg,
        'req_count_avg': req_count_avg,
        'resp_time_avg': resp_time_avg,
        'req_count_probs_weighted': req_count_probs_weighted,
    }

