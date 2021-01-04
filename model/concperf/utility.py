import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import scipy.stats as stats

# fit a normal distribution, number_count is how many we want to average


def get_normal_dist_params(vals, probs, number_count=1, ):
    # mean stays the same
    normal_mean = np.sum(np.array(vals) * np.array(probs))
    # average n values, variance is divided by n
    normal_variance = np.sum(
        np.power(vals - normal_mean, 2) * probs) / number_count
    return normal_mean, np.sqrt(normal_variance)

# plot a normal fit for the data, given values, probs, and how many we average over


def plot_normal_fit(vals, probs, avg_count, label='Normal Distribution Fit'):
    normal_mean, normal_std = get_normal_dist_params(vals, probs, avg_count)
    plt_x_vals = np.linspace(normal_mean - 3 * normal_std,
                             normal_mean + 3 * normal_std, 100)
    # calculate the value of distribution in different configs
    dist_vals = np.array(
        [stats.norm.pdf(x, loc=normal_mean, scale=normal_std) for x in plt_x_vals])
    plt.plot(plt_x_vals, dist_vals, label=label)

# calculate probability for adding valuees with similar distribution


def get_averaged_distribution(vals, probs, avg_count=2, prune_val=1e-6):
    dist = {vals[i]: probs[i] for i in range(len(vals))}

    for _ in range(avg_count-1):
        # single addition
        new_dist = {}
        for (val, prob) in zip(vals, probs):
            for k in dist:
                prob_val = prob * dist[k]
                if not (k+val) in new_dist:
                    new_dist[k+val] = 0

                new_dist[k+val] += prob_val
        dist = new_dist
        # prune low probability dists
        if prune_val is not None:
            remove_keys = [k for k in dist.keys() if dist[k] < prune_val]
            for k in remove_keys:
                del dist[k]

    # values and probabilities
    return np.array(list(dist.keys()))/avg_count, np.array(list(dist.values()))


def solve_CTMC(Q):
    # solve CTMC for pi
    state_count = Q.shape[0]
    Q[:, 0] = 1
    y = np.zeros((1, Q.shape[0]))
    y[0, 0] = 1
    solution = np.linalg.solve(np.array(Q.T), np.array(y.T))
    solution = solution.reshape(solution.shape[0],)
    solution[solution < 0] = 0
    return solution


def get_trans_probs(state_count, transition_rate_base, max_t=2):
    next_ready_counts = list(range(state_count))
    next_ready_counts = np.array(next_ready_counts)
    trans_rates = (next_ready_counts + 1) * transition_rate_base

    Q = np.zeros((state_count, state_count))
    # our initial state
    init_state = np.zeros(state_count)
    init_state[0] = 1

    for i in range(0, state_count-1):
        Q[i, i+1] = trans_rates[i]
        Q[i, i] = -1 * trans_rates[i]

    solution = init_state @ sp.linalg.expm(Q * max_t)
    return solution
