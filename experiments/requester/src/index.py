from workload import *
import util
import pytz
from datetime import datetime

import pandas as pd
# tqdm to monitor progress
from tqdm.auto import tqdm
tqdm.pandas()

# import my own modules
from pacswg.timer import *
import pacswg

my_timezone = os.getenv('PY_TZ', 'US/Eastern')

print('*** Clearing logger before getting started ***')
util.clear_logger()

def perform_experiment():
    wg = pacswg.WorkloadGenerator(worker_func=worker_func, rps=0, worker_thread_count=100)
    wg.start_workers()
    timer = TimerClass()

    print("============ Experiment Started ============")
    print("Time Started:", datetime.now().astimezone(pytz.timezone(my_timezone)))

    for rps in tqdm(rps_list):
        wg.set_rps(rps)
        timer.tic()
        while timer.toc() < (time_per_step):
            wg.fire_wait()

    wg.stop_workers()
    all_res = wg.get_stats()
    print("Total Requests Made:", len(all_res))

    # Save The Results
    df_res = pd.DataFrame(data=all_res)
    now = datetime.now()
    csv_filename = now.strftime('res-%Y-%m-%d_%H-%M-%S.csv')
    df_res.to_csv(os.path.join('results', csv_filename))

    print("CSV File Name:", csv_filename)

def smooth_out_rps(tmp_rps_list):
    # smooth it out
    rps_list = []
    for r in tmp_rps_list:
        if len(rps_list) > 0:
            rps_list.append((r + rps_list[-1])/2)        
        rps_list.append(r)
    return rps_list


if __name__ == '__main__':
    time_per_step = 60
    #rps_list = [2,2,2]
    rps_list = [2] * 60

    perform_experiment()
