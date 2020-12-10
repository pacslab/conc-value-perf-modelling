# importas
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import requests
from datetime import datetime
import pytz

# constants
logger_path = os.getenv('LOGGER_PATH', 'http://172.17.0.1:3000')
exp_name = os.getenv('EXPERIMENT_NAME', 'DEFAULT_EXPERIMENT')
my_timezone = os.getenv('PY_TZ', 'US/Eastern')

# plotting and analyzing functionality
def init_plot():
  plt.figure(figsize=(10,4))
  plt.tight_layout()

def plot_hist(x, y, title='concurrency level histogram'):
  init_plot()
  plt.title(title)
  plt.bar(x, y)

def convert_timestamp(ts):
  return datetime.fromtimestamp(ts/1000).astimezone(pytz.timezone(my_timezone)).replace(tzinfo=None)

def print_current_conc_stat():
  res = get_current_conc_stat()
  print(f"average concurrency: {res['avg']}")
  print(f"running instances: {res['running_instance_count']}")
  if 'report_time' in res:
    print(f"report time: {convert_timestamp(res['report_time'])}")
  print(res['x'])
  print(res['y'])
  plot_hist(res['x'], res['y'])

def convert_hist_to_values(h):
  # get values based on estimated hist fetched
  values = []
  for x,y in zip(h['x'], h['y']):
    values += [x] * int(y)
  return values

def parse_csv_file(csv_file):
    df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    df['client_elapsed_time'] = df['client_elapsed_time'] * 1000
    epoch_cols_list = ['client_start_time', 'client_end_time',]
    datetimes = {}
    for epoch_col in epoch_cols_list:
        times = df[epoch_col].apply(lambda x: datetime.fromtimestamp(x).astimezone(pytz.timezone(my_timezone)).replace(tzinfo=None))
        times = pd.to_datetime(times.dt.to_pydatetime())
        df[epoch_col + '_dt'] = times
        datetimes[epoch_col] = times

    df = df.set_index('client_start_time_dt')
    return df


if __name__ == "__main__":
    csv_file = 'results/res-2020-12-09_02-37-24.csv'
    fig_folder = 'figs/'
    df = parse_csv_file(csv_file)
    print(df.head())

    init_plot()
    df['client_elapsed_time'][100:].resample('10s').mean().plot()
    df['client_elapsed_time'].mean()
    plt.savefig(fig_folder + 'resp.png', dpi=600)
