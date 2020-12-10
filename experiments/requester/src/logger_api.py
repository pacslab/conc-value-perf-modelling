import os
import json
import requests
import pandas as pd

from plot_results import convert_timestamp

logger_path = os.getenv('LOGGER_PATH', 'http://172.17.0.1:3000')
exp_name = os.getenv('EXP_NAME', 'DEFAULT_EXPERIMENT')

# logger functionality
def get_current_conc_stat():
  url = f'{logger_path}/logger/conc_logs/{exp_name}/last'
  print(f'fetching {url}')
  res = requests.get(url)
  res = res.json()
  return res

def get_conc_log_history():
  url = f'{logger_path}/logger/conc_logs/{exp_name}'
  print(f'fetching {url}')
  res = requests.get(url)
  res = res.json()
  return res

def get_conc_history_df(conc_data):
    df = pd.DataFrame(data=conc_data)
    df['report_time'] = df['report_time'].apply(lambda x: convert_timestamp(x))
    return df

def get_long_term_stats():
  url = f'{logger_path}/logger/experiment_logs/{exp_name}/stats'
  print(f'fetching {url}')
  res = requests.get(url)
  res = res.json()
  return res

def save_json_file(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def load_json_file(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data



if __name__ == "__main__":
    conc_data = get_conc_log_history()
    stats_data = get_long_term_stats()

    save_json_file(conc_data, 'results/test1.json')
    save_json_file(stats_data, 'results/test2.json')

    # conc_df = get_conc_history_df(conc_data)
    # print(conc_df.head())
