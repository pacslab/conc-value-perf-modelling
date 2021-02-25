# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# # Experimenting With APIs
# 
# In this notebook, we will be experimenting with the APIs and create helper functions.

# %%
# general imports
import time
import copy
from datetime import datetime
import pytz
import os

my_timezone = os.getenv('PY_TZ', 'America/Toronto')

# library imports
from tqdm.auto import tqdm
import pandas as pd
import numpy as np

# my library imports
from pacswg.timer import TimerClass
import pacswg

# my imports
from helpers import kube

# %% [markdown]
# ## Kubernetes API
# 
# We use the kubernetes API to fetch the current status of each deployment and see how many instances they have.

# %%
# start watch thread
kube.start_watch_thread()
# print details of a deployment
# print(kube.live_deployments['helloworld-go-00001-deployment'])
# fetch a list of all knative deployments
# print(kube.get_knative_deployments())
# fetch latest revisions only

def get_knative_watch_info(kn_deploy_name):
    kn_latest_revs = kube.get_kn_latest_revs()
    if kn_deploy_name not in kn_latest_revs:
        return None
    bench_deployment = kn_latest_revs[kn_deploy_name]
    return kube.live_deployments[bench_deployment.deployment]

# get_knative_watch_info('bench1')

# %%

def kn_change_opts_target(new_target, workload_spec):
    # workload_spec['opts']['--concurrency-target'] = new_target
    workload_spec['annotations']['autoscaling.knative.dev/target'] = new_target
    return workload_spec

def get_time_with_tz():
    return datetime.now().astimezone(pytz.timezone(my_timezone))

# %% [markdown]
# # Specifying Single Experiment
# 
# In this section, we will build the foundation for running a single experiment. In a later section, we will
# run several experiments to collect the necessary data.

# %%
def perform_experiment(rps, target, base_workload_spec, wlogger):
    exp_spec = base_workload_spec['exp_spec']
    rps_list = [rps] * exp_spec['time_mins']
    # get base workload
    workload_spec = copy.deepcopy(base_workload_spec)
    worker_func = workload_spec['simple_worker_func']
    del workload_spec['simple_worker_func']
    # change base workload target
    kn_change_opts_target(target, workload_spec)
    # get kn command to change target
    kn_command = kube.get_kn_command(**workload_spec)
    print('applying kn command:')
    print(kn_command)
    # apply the kn command
    get_ipython().system('{kn_command}')
    # wait for kn command to take effect
    time.sleep(10)
    print('kn apply done')

    # initialize
    wg = pacswg.WorkloadGenerator(worker_func=worker_func, rps=0, worker_thread_count=100)
    wg.start_workers()
    timer = TimerClass()
    # make sure that logger is stopped
    wlogger.stop_capturing()
    # start capturing
    wlogger.start_capturing()

    print("============ Experiment Started ============")
    print("Time Started:", get_time_with_tz())

    # for rps in tqdm(rps_list):
    for rps in rps_list:
        wg.set_rps(rps)
        timer.tic()
        # apply each for one minute
        while timer.toc() < 60:
            wg.fire_wait()

    # get the results
    wg.stop_workers()
    all_res = wg.get_stats()
    print("Total Requests Made:", len(all_res))
    wlogger.stop_capturing()
    logger_data = wlogger.get_recorded_data()

    # collect the results
    df_res = pd.DataFrame(data=all_res)
    df_res['rps'] = rps
    df_res['target'] = target
    df_logger = pd.DataFrame(data=logger_data)
    df_logger['rps'] = rps
    df_logger['target'] = target
    now = get_time_with_tz()
    res_name = now.strftime('res-%Y-%m-%d_%H-%M-%S')
    res_folder = f'results/{exp_spec["name"]}/'
    # make the directory and file names
    get_ipython().system('mkdir -p {res_folder}')
    requests_results_filename = f'{res_name}_reqs.csv'
    logger_results_filename = f'{res_name}_logger.csv'
    # save the results
    df_res.to_csv(os.path.join(res_folder, requests_results_filename))
    df_logger.to_csv(os.path.join(res_folder, logger_results_filename))

    print('Experiment Name:', exp_spec['name'])
    print('Results Name:', res_name)

    return res_name


