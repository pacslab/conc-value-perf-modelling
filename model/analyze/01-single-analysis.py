# %% Imports
import sys

import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd
import itertools
from tqdm.auto import tqdm

# import concperf by adding its path
sys.path.append('..')
from concperf import single_model
from concperf import utility

# %% create config

config = {
    "base_service_time": 1,
    "alpha": 1,
    "max_conc": 100,
    "arrival_rate_server": 1,
}

figs_folder = 'figs/'
results_folder = 'results/'

# %% adding functionality for solving for a specific configuration
def process_config(config, arrival_rate, alpha):
    model_config = { **config }
    model_config.update({
        "arrival_rate_server": arrival_rate, 
        "alpha": alpha,
    })

    single_coder = single_model.StateCoder(config=model_config)
    Q = single_model.get_single_container_q(single_coder, config=model_config)

    # for steady-state probability:
    # req_count_prob = utility.solve_CTMC(Q)

    # for transient solution:
    # our initial state
    state_count = Q.shape[0]
    init_state = np.zeros(state_count)
    init_state[0] = 1

    max_t = 60
    state_probs = init_state @ sp.linalg.expm(Q * max_t)
    state_req_counts = [s[0] for s in single_coder.get_state_list()]
    req_count_avg = (state_probs * state_req_counts).sum()

    return {
        "state_probs": state_probs,
        "state_req_counts": state_req_counts,
        "req_count_avg": req_count_avg,
        "arrival_rate": arrival_rate,
        "alpha": alpha,
    }

# print the keys
process_config(config, 1, 1).keys()
# %% process for different values
from concurrent.futures import ProcessPoolExecutor, as_completed

if __name__ == "__main__":
    arrival_rates = np.linspace(0.1, 20, 100)
    alphas = [0.01, 0.05, 0.1, 0.5, 1]
    df_data = itertools.product(arrival_rates, alphas)

    futures = []
    with ProcessPoolExecutor(max_workers=1) as pool:
        for arrival_rate, alpha in df_data:
            future = pool.submit(process_config, config, arrival_rate, alpha)
            futures.append(future)
        
    # get the future results as they are completed
    results = [f.result() for f in as_completed(futures)]

# %% create plots

def save_fig(figname):
    plt.savefig(figs_folder + figname + ".png", dpi=600)
    plt.savefig(figs_folder + figname + ".pdf")

if __name__ == "__main__":
    df = pd.DataFrame(results)
    df.to_csv(results_folder + '01_conc_vs_arrival_alpha.csv')
    for alpha in alphas:
        sub_df = df[df['alpha'] == alpha]
        sub_df = sub_df.sort_values('arrival_rate')
        plt.plot(sub_df['arrival_rate'], sub_df['req_count_avg'], label=f"Alpha={alpha}")
        
    plt.ylim((0, 80))
    plt.ylabel('Concurrency')
    plt.xlabel('Arrival Rate Per Container')
    plt.grid(True)
    plt.legend()
    save_fig('01_conc_vs_arrival_alpha')