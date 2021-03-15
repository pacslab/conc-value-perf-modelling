# %% Imports
from IPython import get_ipython
import os
import sys

import numpy as np
import pandas as pd
import itertools
import time
from tqdm.auto import tqdm

import pacsltk.pacs_util as pacs_util
pacs_util.prepare_matplotlib_cycler()

# To avoid type 3 fonts: http://phyletica.org/matplotlib-fonts/
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# import concperf by adding its path
sys.path.append('..')
from concperf import general_model
from concperf import utility
# %% create config

# the target utilization
target_util = 0.7

# exp_config_name = 'bench1_sleep_rand2_1000_200'
# exp_config_name = 'autoscale_go_500_10k_5'
exp_config_name = 'autoscale_go_500_10k_5_rps'
regression_models = {
    'bench1_sleep_rand2_1000_200': {
        'conc_average_model': [0.0, 0.7587030452370006, 0.48814170860140793],
        'resp_time_model': [1.1938101149327398, 0.0843490901255519, 0.07563321033774315],
    },
    'autoscale_go_500_10k_5': {
        'conc_average_model': [0.0, 0.49571552241745126, 0.002405756265780249],
        'resp_time_model': [0.516308531798091, -0.00020302040907105838, 2.5159722316614887e-05],
    },
    'autoscale_go_500_10k_5_rps': {
        'conc_average_model': [0.0, 1, 0],
        'resp_time_model': [0.5160698977067653, 0.0018574299435555192, -0.00024075524479620354],
    }
}

# trying new model extracted params
model_config = {
    # 'instance_count' should be added for each state
    # 'arrival_rate_total' should be added for each configuration
    'max_conc': 10,
    'max_container_count': 60,
    # 'target_conc': 9*target_util, # assumes target utilization
    'max_scale_up_rate': 1000, # from N to 1000*N at most
    'max_scale_down_rate': 2, # from N to N/2 at most
    'autoscaling_interval': 2, # amount of time between autoscaling evaluations
    'provision_rate_base': 1,
    'deprovision_rate_base': 2,
    # new regression settings
    # bench1_sleep_rand2_1000_200
    'conc_average_model': regression_models[exp_config_name]['conc_average_model'],
    'resp_time_model': regression_models[exp_config_name]['resp_time_model'],
}

def update_config(config):
    config['arrival_rate_server'] = config['arrival_rate_total'] / config['instance_count']

figs_folder = 'figs/'
results_folder = 'results/'
# %%
def parse_arrival_rate(arrival_rate, target_conc, model_config, target_util=0.7):
    config = {**model_config}
    config.update({
        'arrival_rate_total': arrival_rate,
        'target_conc': target_conc*target_util,
    })
    res = general_model.solve_general_model(config, update_config)
    res_params = general_model.calculate_general_params(res, config)
    res.update(res_params)
    res.update(config)
    return res

parse_arrival_rate(1, 1, model_config, target_util).keys()

# %% process for different values
from concurrent.futures import ProcessPoolExecutor, as_completed

if __name__ == "__main__":
    arrival_rates = [1,2,3,5,7,10,15,20]
    target_concs = [1,2,3,5,7,10]
    plot_targets = [1,2,5,10]
    df_data = list(itertools.product(arrival_rates, target_concs))

    start_time = time.time()

    futures = []
    with ProcessPoolExecutor(max_workers=1) as pool:
        for arrival_rate, target_conc in df_data:
            future = pool.submit(parse_arrival_rate, arrival_rate, target_conc, model_config, target_util)
            futures.append(future)
        
    # get the future results as they are completed
    total_results = [f.result() for f in as_completed(futures)]
    elapsed_time = time.time() - start_time
    print(f"\nnew order calculation took {elapsed_time:4.2f} seconds for {len(df_data)} arrival rates ({elapsed_time/len(df_data):4.2f} per job)")

# %% extract the fields we are interested in from the results
if __name__ == "__main__":
    extract_keys = [
        'arrival_rate_total', 
        'ready_avg', 
        'ordered_avg', 
        'req_count_avg', 
        'resp_time_avg',
        'target_conc',
    ]

    def extract_params(total_results, target_util=0.7):
        extract_vals = []
        for r in total_results:
            extract_vals.append({k:r[k] for k in extract_keys})
        resdf = pd.DataFrame(data=extract_vals)
        resdf['cc'] = (resdf['target_conc']/target_util)
        return resdf


    resdf = extract_params(total_results)
    print(resdf.head())

# %% Save for later use
save_results_folder = f"{results_folder}{exp_config_name}/"
get_ipython().system('mkdir -p {save_results_folder}')
resdf.to_csv(f"{save_results_folder}res_df.csv")

# %% [markdown]
# # Overall Arrival Rate Plots
# %% prepare for plots

# Prepare for plots and make directories
figs_folder = "./figs/"
get_ipython().system('mkdir -p {figs_folder}')

# get paths for a figure
def get_fig_path(x, exp_name):
    return (os.path.join(figs_folder , exp_name, x + ".png"), os.path.join(figs_folder, exp_name, x + ".pdf"))

# save figure
def tmp_fig_save(fig_name, exp_name):
    get_ipython().system(f'mkdir -p {figs_folder}{exp_name}')
    paths = get_fig_path(fig_name, exp_name)
    plt.savefig(paths[0], dpi=600)
    plt.savefig(paths[1])

def default_plt_configs(figsize=(8,4), xlabel='Arrival Rate (reqs/s)'):
    plt.figure(figsize=figsize)
    plt.grid(True)
    plt.tight_layout()
    plt.xlabel(xlabel)
# %% make ready container plots
if __name__ == "__main__":
    rps_ticks = arrival_rates

    default_plt_configs(figsize=(4,2.5))
    for target_conc in target_concs:
        if target_conc in plot_targets:
            sub_df = resdf.loc[np.abs(resdf['cc'] - target_conc) < 0.01, :]
            sub_df = sub_df.sort_values('arrival_rate_total')
            plt.plot(sub_df['arrival_rate_total'], sub_df['ready_avg'], label=f'Target={target_conc}')
    plt.legend()
    plt.gca().set_xscale('log')
    plt.xticks(rps_ticks, rps_ticks)
    plt.ylabel("Average Ready Containers")
    plt.gcf().subplots_adjust(left=0.16, bottom=0.20)
    tmp_fig_save('01_average_ready_containers_vs_arrival_rate', exp_config_name)
# %% make average concurrency plot
if __name__ == "__main__":
    rps_ticks = arrival_rates

    default_plt_configs(figsize=(4,2.5))
    for target_conc in target_concs:
        if target_conc in plot_targets:
            sub_df = resdf.loc[np.abs(resdf['cc'] - target_conc) < 0.01, :]
            sub_df = sub_df.sort_values('arrival_rate_total')
            plt.plot(sub_df['arrival_rate_total'], sub_df['req_count_avg'], label=f'Target={target_conc}')
    plt.legend()
    plt.gca().set_xscale('log')
    plt.xticks(rps_ticks, rps_ticks)
    plt.ylabel("Average Concurrency")
    plt.gcf().subplots_adjust(left=0.13, bottom=0.20)
    tmp_fig_save('02_conc_window_average_vs_arrival_rate', exp_config_name)
# %% make average response time plot
if __name__ == "__main__":
    rps_ticks = arrival_rates

    default_plt_configs(figsize=(4,2.5))
    for target_conc in target_concs:
        if target_conc in plot_targets:
            sub_df = resdf.loc[np.abs(resdf['cc'] - target_conc) < 0.01, :]
            sub_df = sub_df.sort_values('arrival_rate_total')
            plt.plot(sub_df['arrival_rate_total'], sub_df['resp_time_avg'], label=f'Target={target_conc}')
    plt.legend()
    plt.gca().set_xscale('log')
    plt.xticks(rps_ticks, rps_ticks)
    plt.ylabel("Average Response Time (s)")
    plt.gcf().subplots_adjust(left=0.13, bottom=0.20)
    tmp_fig_save('03_average_resp_time_vs_arrival_rate', exp_config_name)
# %% make twinx plot
# let's see if we can make plots for effect of CC
from matplotlib import ticker

for plot_arrival_rate in [1,2,5,10,20]:
    sub_overview_df = resdf[resdf['arrival_rate_total'] == plot_arrival_rate]
    sub_overview_df = sub_overview_df.sort_values('cc')
    # to have the same values we had in experiments
    # sub_overview_df = sub_overview_df[sub_overview_df['cc'].isin([1,2,5,10])]

    plt.figure(figsize=(4,2.5))
    color = 'k'
    ax1 = plt.gca()
    ax1.plot(sub_overview_df['cc'], sub_overview_df['ready_avg'], color=color)
    ax1.set_xlabel('Target Value')
    ax1.set_ylabel('Instance Count', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.grid(True, axis='x')

    color = 'tab:red'
    ax2 = plt.gca().twinx()
    ax2.plot(sub_overview_df['cc'], sub_overview_df['resp_time_avg'], ls='--', color=color)
    ax2.set_ylabel('Response Time (s)', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid(None)
    # ax2.set_ylim([0.4,0.6])

    # aligning ticks for grids
    l = ax1.get_ylim()
    l2 = ax2.get_ylim()
    f = lambda x : l2[0]+(x-l[0])/(l[1]-l[0])*(l2[1]-l2[0])
    ticks = f(ax1.get_yticks())
    ax2.yaxis.set_major_locator(ticker.FixedLocator(ticks))

    # final config
    plt.gcf().subplots_adjust(left=0.13, bottom=0.20)
    plt.tight_layout()

    tmp_fig_save(f'04_inst_count_resp_time_target_arrival_{plot_arrival_rate}', exp_config_name)
# %%
