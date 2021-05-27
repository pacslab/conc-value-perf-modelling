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
# %%
exp_config_name = 'bench1_sleep_rand2_1000_200'
# exp_config_name = 'autoscale_go_500_10k_5'
# exp_config_name = 'autoscale_go_500_10k_5_rps'
# exp_config_name = 'bench1_cpu_io_rps'

figs_folder = 'figs/'
results_folder = 'results/'

get_ipython().system('mkdir -p {figs_folder}')

# get paths for a figure


def get_fig_path(x, exp_name):
    return (os.path.join(figs_folder, exp_name, x + ".png"), os.path.join(figs_folder, exp_name, x + ".pdf"))

# save figure


def tmp_fig_save(fig_name, exp_name):
    get_ipython().system(f'mkdir -p {figs_folder}{exp_name}')
    paths = get_fig_path(fig_name, exp_name)
    plt.savefig(paths[0], dpi=600)
    plt.savefig(paths[1])


# %%
# let's see if we can make plots for effect of CC
from matplotlib import ticker

# model file
results_file_name = f"{results_folder}{exp_config_name}/res_df.csv"
resdf = pd.read_csv(results_file_name)
# experiment file
results_exp_file_name = f"{results_folder}{exp_config_name}/res_df_exp.csv"
orig_overview_parsed_df = pd.read_csv(results_exp_file_name)


plot_arrival_rates = [1,2,5,10,20]
for plot_arrival_rate in plot_arrival_rates:
    sub_overview_df = resdf[resdf['arrival_rate_total'] == plot_arrival_rate]
    sub_overview_df = sub_overview_df.sort_values('cc')
    # experiment file
    sub_overview_df_exp = orig_overview_parsed_df[orig_overview_parsed_df['rps'] == plot_arrival_rate]

    plt.figure(figsize=(4,2.5))
    color = 'k'
    ax1 = plt.gca()
    lns1 = ax1.plot(sub_overview_df['cc'], sub_overview_df['ready_avg'], color=color, label='Model Count')
    lns2 = ax1.errorbar(sub_overview_df_exp['target'], sub_overview_df_exp['average_ready_count_mean'], ls='--', yerr=sub_overview_df_exp['average_ready_count_ci'], label='Exp Count')
    # lns2 = ax1.plot(sub_overview_df_exp['target'], sub_overview_df_exp['average_ready_count_mean'], ls='--', label='Exp Count')
    ax1.set_xlabel('Target Value')
    ax1.set_ylabel('Instance Count', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.grid(True, axis='x')

    color = 'tab:red'
    ax2 = plt.gca().twinx()
    lns3 = ax2.plot(sub_overview_df['cc'], sub_overview_df['resp_time_avg'], ls='-', color=color, label='Model RT')
    lns4 = ax2.errorbar(sub_overview_df_exp['target'], sub_overview_df_exp['client_elapsed_time_mean'], yerr=sub_overview_df_exp['client_elapsed_time_ci'], ls='--', label='Exp RT')
    # lns4 = ax2.plot(sub_overview_df_exp['target'], sub_overview_df_exp['client_elapsed_time_mean'], ls='--', label='Exp RT')
    ax2.set_ylabel('Response Time (s)', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid(None)
    # ax2.set_ylim([0.4,0.6])
    # ax2.set_ylim([0.1,0.4])

    # aligning ticks for grids
    l = ax1.get_ylim()
    l2 = ax2.get_ylim()
    f = lambda x : l2[0]+(x-l[0])/(l[1]-l[0])*(l2[1]-l2[0])
    ticks = f(ax1.get_yticks())
    ax2.yaxis.set_major_locator(ticker.FixedLocator(ticks))

    # final config
    plt.gcf().subplots_adjust(left=0.13, bottom=0.20)
    plt.tight_layout()
    
    # fix for error bars for marged labels
    lns2 = [lns2]
    lns4 = [lns4]
    
    # merging labels
    lns = lns1+lns2+lns3+lns4
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=0)

    tmp_fig_save(f'05_inst_count_resp_time_target_arrival_{plot_arrival_rate}_double', exp_config_name)

# %%
