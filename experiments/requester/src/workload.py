#! /usr/local/bin/python

import os
import sys
import time

import requests

http_path = os.getenv('HTTP_PATH')

if http_path is None:
    print("HTTP_PATH environment variable is necessary!")
    sys.exit(1)

print("Loaded HTTP path:", http_path)

def worker_func():
    cmds = {}
    cmds['sleep'] = 0
    cmds['sleep_till'] = 0
    cmds['stat'] = {"argv": 1}

    cmds['cpu'] = {"n": 20000}

    # cmds['io'] = {"rd": 3, "size": "200K", "cnt": 5}
    # cmds['cpu'] = {"n": 10000}

    payload = {}
    payload['cmds'] = cmds

    client_start_time = time.time()
    res = requests.post(http_path, json=payload)
    client_end_time = time.time()
    r_parsed = res.json()

    if "stat" not in r_parsed or r_parsed['stat'] is None:
        print(r_parsed)

    return {
        # this doesn't work with cloud run
        'is_cold': r_parsed['stat']['exist_id'] == r_parsed['stat']['new_id'],
        'client_start_time': client_start_time,
        'client_end_time': client_end_time,
        'client_elapsed_time': client_end_time - client_start_time,
    }

if __name__ == '__main__':
    print(worker_func())
