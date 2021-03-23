
import requests
import random

def bench1_sleep_rand2(sleep_base, sleep_rand):
    http_path = "http://bench1.default.kn.nima-dev.com"

    cmds = {}
    cmds['sleep'] = 0
    cmds['sleep_till'] = 0
    cmds['stat'] = {"argv": 1}

    # cmds['cpu'] = {"n": 5000}

    cmds['sleep'] = sleep_base + (random.random() * sleep_rand)

    # cmds['io'] = {"rd": 3, "size": "200K", "cnt": 5}
    # cmds['cpu'] = {"n": 10000}

    payload = {}
    payload['cmds'] = cmds

    res = requests.post(http_path, json=payload)
    if res.status_code >= 300:
        return False
    return True

def bench1_cpu_io():
    http_path = "http://bench1.default.kn.nima-dev.com"

    cmds = {}
    cmds['sleep'] = 0
    cmds['sleep_till'] = 0
    cmds['stat'] = {"argv": 1}

    cmds['io'] = {"rd": 3, "size": "200K", "cnt": 2}
    cmds['cpu'] = {"n": 10000}

    payload = {}
    payload['cmds'] = cmds

    res = requests.post(http_path, json=payload)
    if res.status_code >= 300:
        return False
    return True

def autoscale_go_workload_func(sleep="500", prime="10000", bloat="5"):
    http_path = "http://autoscale-go.default.kn.nima-dev.com"

    params = {
        "sleep": sleep,
        "prime": prime,
        "bloat": bloat,
    }

    http_path += "?"
    for k,v in params.items():
        http_path += f"{k}={v}&"

    res = requests.get(http_path)
    if res.status_code >= 300:
        return False
    return True


workload_funcs = {
    "autoscale_go_500_10k_5": lambda: autoscale_go_workload_func(sleep="500", prime="10000", bloat="5"),
    "autoscale_go_500_10k_5_rps": lambda: autoscale_go_workload_func(sleep="500", prime="10000", bloat="5"),
    "bench1_sleep_rand2_1000_200": lambda: bench1_sleep_rand2(sleep_base=1000, sleep_rand=200),
    "bench1_cpu_io_rps": bench1_cpu_io,
}
