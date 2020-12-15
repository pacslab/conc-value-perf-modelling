from workload import *
import logger_api
import util
import pytz
import sys
import time
from datetime import datetime

import pandas as pd
# tqdm to monitor progress
from tqdm.auto import tqdm
tqdm.pandas()

# import my own modules
from pacswg.timer import *
import pacswg

my_timezone = os.getenv('PY_TZ', 'US/Eastern')

def perform_experiment(rps_list, info_data):
    print('*** Clearing logger before getting started ***')
    util.clear_logger()
    reset_conc()

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
    res_name = now.strftime('res-%Y-%m-%d_%H-%M-%S')
    csv_filename = res_name + '.csv'
    df_res.to_csv(os.path.join('results', csv_filename))
    # get logger logs and save as json
    conc_data = logger_api.get_conc_log_history()
    conc_file_path = os.path.join('results', res_name + '_conc.json')
    logger_api.save_json_file(conc_data, conc_file_path)
    # get stats
    stats_data = logger_api.get_long_term_stats()
    stats_file_path = os.path.join('results', res_name + '_stats.json')
    logger_api.save_json_file(stats_data, stats_file_path)

    info_file_path = os.path.join('results', res_name + '_info.json')
    logger_api.save_json_file(info_data, info_file_path)

    print("CSV File Name:", csv_filename)
    print("Conc JSON File:", conc_file_path)
    print("Stats JSON File:", stats_file_path)

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
    # rps_list = [2,2,2]
    # rps_list = [i for i in range(1, 5)] + [5] * 60
    # rps_list = [5] * 60

    if len(sys.argv) < 4:
        print('please provide the set concurrency target on the server')
        print('python index.py concurrency_target(no default) concurrency_limit(0 default) concurrency_target_utilization(70 default)')
        sys.exit(1)
    
    # build info
    info_data = {}
    info_data['concurrency_target'] = float(sys.argv[1])
    info_data['concurrency_limit'] = float(sys.argv[2])
    info_data['concurrency_target_utilization'] = float(sys.argv[3])

    # start concurrency report thread
    t1 = threading.Thread(target=report_conc_loop, args=(), daemon=True)
    t1.start()


    for _ in range(3):
        for rps in list(range(1,11)) + list(range(15, 41, 5)):
            rps_list = [rps] * 20

            info_data['rps_list'] = rps_list

            print(info_data)
            perform_experiment(rps_list, info_data)

        # wait to get back to initial state
        time.sleep(3*60)
