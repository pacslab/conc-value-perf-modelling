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
import re
from collections import namedtuple, deque
import random
import copy
from datetime import datetime
import pytz
import os

my_timezone = os.getenv('PY_TZ', 'America/Toronto')

# library imports
import requests
from tqdm.auto import tqdm
import pandas as pd
import numpy as np

# my library imports
from pacswg.timer import TimerClass
import pacswg

# my imports
from helpers import kube
from helpers import workload

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

get_knative_watch_info('bench1')

# %% [markdown]
# ## Deploying On Knative
# 
# In this section, we will develop the functionality to deploy a given workload to **knative** using the `kn` CLI.
# The other options were using [CRDs](https://stackoverflow.com/questions/61384188/how-to-deploy-a-knative-service-with-kubernetes-python-client-library),
# or using [kubectl apply](https://developers.redhat.com/coderland/serverless/deploying-serverless-knative#invoking_your_service_from_the_command_line)
# but `kn` seems to be more powerful.

# %%
# making sure kn is set up correctly
get_ipython().system('kn service ls')


# %%
# workload_name = 'bench1'
workload_name = 'autoscale-go'
# image = 'ghcr.io/nimamahmoudi/conc-workloads-bench1:sha-5966a0e'
image = 'gcr.io/knative-samples/autoscale-go:0.1'
env = {
    'EXPERIMENT_NAME': 'TEST1',
    'REPORT_INTERVAL': '10',
    'SOCKETIO_SERVER': 'NO',
}
opts = {
    '--limit': "'cpu=250m,memory=256Mi'",
    '--concurrency-target': '1',
    # '--concurrency-limit': '10',
    # '--concurrency-utilization': '70',
    # '--autoscale-window': '60s',
}
annotations = {
    'autoscaling.knative.dev/panicThresholdPercentage': '1000',
}

workload_spec = {
    'name': workload_name,
    'image': image,
    'env': env,
    'opts': opts,
    'annotations': annotations,
}

def kn_change_opts_concurrency_target(new_target, workload_spec):
    workload_spec['opts']['--concurrency-target'] = new_target
    return opts

# to change options to have a new concurrency target
# kn_change_opts_concurrency_target(1, workload_spec)

kn_command = kube.get_kn_command(**workload_spec)
print(kn_command)
# to run the command, we can simply use:
# !{kn_command}

# %% [markdown]
# # Workload Specification

# %%
# user defined workload function
# def user_workload_func():
#     http_path = "http://bench1.default.kn.nima-dev.com"

#     cmds = {}
#     cmds['sleep'] = 0
#     cmds['sleep_till'] = 0
#     cmds['stat'] = {"argv": 1}

#     cmds['cpu'] = {"n": 5000}

#     # cmds['sleep'] = 1000 + (random.random() * 200)
#     # cmds['sleep'] = 400 + (random.random() * 200)

#     # cmds['io'] = {"rd": 3, "size": "200K", "cnt": 5}
#     # cmds['cpu'] = {"n": 10000}

#     payload = {}
#     payload['cmds'] = cmds

#     res = requests.post(http_path, json=payload)
#     if res.status_code >= 300:
#         return False
#     return True

def user_workload_func():
    http_path = "http://autoscale-go.default.kn.nima-dev.com"

    params = {
        "sleep": "500",
        "prime": "10000",
        "bloat": "5",
    }

    http_path += "?"
    for k,v in params.items():
        http_path += f"{k}={v}&"

    res = requests.get(http_path)
    if res.status_code >= 300:
        return False
    return True

# get ready count callback
get_ready_cb = lambda: get_knative_watch_info(workload_name)['ready_replicas']
print('ready callback:', get_ready_cb())
# create logger and check one execution of workload func
wlogger = workload.WorkloadLogger(get_ready_cb=get_ready_cb)
simple_worker_func = lambda: wlogger.worker_func(user_workload_func)
# add worker func to workload spec
workload_spec['simple_worker_func'] = simple_worker_func

simple_worker_func()


# %%
# wlogger.monitoring_thread.start()
# wlogger.record_conc_loop()
# wlogger.monitor_conc_loop()
wlogger.start_capturing()
time.sleep(7)
wlogger.stop_capturing()
wlogger.get_recorded_data()

# %% [markdown]
# # Specifying Single Experiment
# 
# In this section, we will build the foundation for running a single experiment. In a later section, we will
# run several experiments to collect the necessary data.

# %%
def perform_experiment(rps, cc, base_workload_spec, exp_spec):
    rps_list = [rps] * exp_spec['time_mins']
    # get base workload
    workload_spec = copy.deepcopy(base_workload_spec)
    worker_func = workload_spec['simple_worker_func']
    del workload_spec['simple_worker_func']
    # change base workload cc
    kn_change_opts_concurrency_target(cc, workload_spec)
    # get kn command to change cc
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
    print("Time Started:", datetime.now().astimezone(pytz.timezone(my_timezone)))

    for rps in tqdm(rps_list):
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
    df_res['cc'] = cc
    df_logger = pd.DataFrame(data=logger_data)
    df_logger['rps'] = rps
    df_logger['cc'] = cc
    now = datetime.now().astimezone(pytz.timezone(my_timezone))
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


# experiment specification
exp_spec = {
    'time_mins': 20,
    'name': 'autoscale_go_500_10k_5',
}

# cc_list = range(1,10,2)
# rps_list = np.linspace(1,21,11)
cc_list = [1,2,5,10]
rps_list = [1,2,5,10,15,20]

# perform_experiment(rps=1, cc=1, base_workload_spec=workload_spec, exp_spec=exp_spec)

# %% [markdown]
# # Performing A Series of Experiments

# %%
# for cc in cc_list:
#     for rps in rps_list:
#         perform_experiment(rps=rps, cc=cc, base_workload_spec=workload_spec, exp_spec=exp_spec)


