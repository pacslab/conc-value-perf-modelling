from IPython import get_ipython

# imports for plots
import pacsltk.pacs_util as pacs_util
import pandas as pd
import numpy as np

pacs_util.prepare_matplotlib_cycler()

# To avoid type 3 fonts: http://phyletica.org/matplotlib-fonts/
from matplotlib import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt

# for fixing tickers
from matplotlib.ticker import ScalarFormatter

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# system imports
import os

# for datetime analysis
from datetime import datetime, timedelta
import pytz

my_timezone = os.getenv('PY_TZ', 'America/Toronto')



# Prepare for plots and make directories
figs_folder = "./figs/"
get_ipython().system('mkdir -p {figs_folder}')


# get paths for a figure
def get_fig_path(x, exp_name):
    return (os.path.join(figs_folder , exp_name, "exp" + x + ".png"), os.path.join(figs_folder, exp_name, "exp" + x + ".pdf"))

# fix log plot on x axis
def fix_log_x_plot():
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())

# fix log plot on y axis
def fix_log_y_plot():
    plt.gca().yaxis.set_major_formatter(ScalarFormatter())

# save figure
def tmp_fig_save(fig_name, exp_name):
    get_ipython().system(f'mkdir -p {figs_folder}{exp_name}/{figs_folder}')
    paths = get_fig_path(fig_name, exp_name)
    plt.savefig(paths[0], dpi=600)
    plt.savefig(paths[1])

# parse epoch columns
def parse_epoch_cols(df, epoch_cols_list):
    for epoch_col in epoch_cols_list:
        times = df[epoch_col].apply(lambda x: datetime.fromtimestamp(x).astimezone(pytz.timezone(my_timezone)).replace(tzinfo=None))
        times = pd.to_datetime(times.dt.to_pydatetime())
        df[epoch_col + '_dt'] = times

# parse single file functions
def parse_logger_file(csv_file_path, parse_skip_mins=0):
    df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
    parse_epoch_cols(df, ['time', ])
    # skip 5 minutes
    df = df[df['time_dt'] > df['time_dt'].min() + timedelta(minutes=parse_skip_mins)]
    # df = df[df['time_dt'] < df['time_dt'].min() + timedelta(minutes=20)]
    df['lambda_over_n'] = df['rps'] / df['ready_count']
    df['current_cc'] = df['total_conc'] / df['ready_count']
    # set index to the time
    df = df.set_index('time_dt')
    return df

# parse in batches with custom functions and return mean, var, and se
def parse_batch_custom_funcs(df, batch_seconds, parse_cols_funcs, start_date=None, stop_date=None):
    if start_date is None:
        start_date = df.index.min()

    if stop_date is None:
        stop_date = df.index.max()

    range_start_dates = pd.date_range(start_date, stop_date,freq=f'{batch_seconds}S')
    # create end dates and drop first and last ones
    range_end_dates = range_start_dates.shift()[1:-1]
    range_start_dates = range_start_dates[1:-1]

    results = {}
    for parse_col_name in parse_cols_funcs:
        val_means = []
        for idx in range(len(range_start_dates)):
            sub_df = df.loc[(df.index < range_end_dates[idx]) & (df.index > range_start_dates[idx]), :]
            val_mean = parse_cols_funcs[parse_col_name](sub_df)
            val_means.append(val_mean)

        val_means_mean = np.mean(val_means)
        val_means_var = np.var(val_means)

        results[f"{parse_col_name}_mean"] = val_means_mean
        results[f"{parse_col_name}_var"] = val_means_var
        results[f"{parse_col_name}_se"] = np.sqrt(val_means_var / len(val_means))

    return results
