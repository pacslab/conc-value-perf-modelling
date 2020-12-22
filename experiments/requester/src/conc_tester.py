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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please provide a name for the concurrency test')
        sys.exit()

    res_name = 'res_' + sys.argv[1]

    all_res = []
    for i in range(1,31,5):
        def conc_worker_func():
            ret = worker_func()
            ret.update({
                'exp_conc': i
            })
            return ret
            
        wg = pacswg.WorkloadGenerator(worker_func=conc_worker_func, rps=0, worker_thread_count=100)
        wg.start_workers()
        timer = TimerClass()

        print(f"============ Experiment Started ({i}) ============")
        print("Time Started:", datetime.now().astimezone(pytz.timezone(my_timezone)))

        # request several times
        for _ in range(10):
            print('.', end='', flush=True)
            for _ in range(i):
                wg.fire()
            time.sleep(.1)
            # wait for all request to go through
            while get_conc() > 0:
                time.sleep(.1)
        print('')

        wg.stop_workers()
        res = wg.get_stats()
        print("Total Requests Made:", len(res))
        all_res += res
    
    # Save The Results
    df_res = pd.DataFrame(data=all_res)
    now = datetime.now()
    csv_filename = res_name + '.csv'
    df_res.to_csv(os.path.join('conc_results', csv_filename))

