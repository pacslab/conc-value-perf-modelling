#! /usr/local/bin/python

import os
import sys
import time
import threading
import random

import requests

from pacswg.timer import *

http_path = os.getenv('HTTP_PATH')
logger_path = os.getenv('LOGGER_PATH')
exp_name = os.getenv('EXP_NAME')

if http_path is None:
    print("HTTP_PATH environment variable is necessary!")
    sys.exit(1)

print("Loaded HTTP path:", http_path)

conc_count = 0
conc_lock = threading.Lock()

def inc_conc():
    global conc_count
    with conc_lock:
        conc_count += 1

def dec_conc():
    global conc_count
    with conc_lock:
        conc_count -= 1

def reset_conc():
    global conc_count
    with conc_lock:
        conc_count = 0

def report_conc_loop():
    global conc_count

    if logger_path is None or exp_name is None:
        print('Report disabled, LOGGER_PATH or EXP_NAME not set.')
        return

    timer = TimerClass()
    while True:
        timer.tic()
        res = requests.post(f'{logger_path}/logger/conc_logs/{exp_name}/client', data={'conc_value': conc_count})
        if res.text != 'OK':
            print('--- client push concurrency failed:', res.status, res.text)
        while timer.toc() < 2:
            time.sleep(0.01)

def worker_func():
    cmds = {}
    # cmds['sleep'] = 400 + (random.random() * 200)
    cmds['sleep'] = 0
    cmds['sleep_till'] = 0
    cmds['stat'] = {"argv": 1}

    cmds['cpu'] = {"n": 20000}

    # cmds['io'] = {"rd": 3, "size": "200K", "cnt": 5}
    # cmds['cpu'] = {"n": 10000}

    payload = {}
    payload['cmds'] = cmds

    inc_conc()
    try:
        start_conc = conc_count
        client_start_time = time.time()
        res = requests.post(http_path, json=payload)
        client_end_time = time.time()
        end_conc = conc_count
        r_parsed = res.json()
    except:
        client_start_time = -1
        client_end_time = -1
        end_conc = -1
    finally:
        dec_conc()

    # if "stat" not in r_parsed or r_parsed['stat'] is None:
    #     print(r_parsed)

    return {
        # this doesn't work with cloud run
        # 'is_cold': r_parsed['stat']['exist_id'] == r_parsed['stat']['new_id'],
        'client_start_time': client_start_time,
        'client_end_time': client_end_time,
        'client_elapsed_time': client_end_time - client_start_time,
        'start_conc': start_conc,
        'end_conc': end_conc,
    }

if __name__ == '__main__':
    print(worker_func())
    # report_conc_loop()
