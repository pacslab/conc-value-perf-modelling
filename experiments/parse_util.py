from IPython import get_ipython

# imports for plots
import pacsltk.pacs_util as pacs_util
import pandas as pd

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
def get_fig_path(x): return (os.path.join(figs_folder, "exp" +
              x + ".png"), os.path.join(figs_folder, "exp" + x + ".pdf"))

# fix log plot on x axis
def fix_log_x_plot():
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())

# fix log plot on y axis
def fix_log_y_plot():
    plt.gca().yaxis.set_major_formatter(ScalarFormatter())

# save figure
def tmp_fig_save(fig_name):
    paths = get_fig_path(fig_name)
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
    # df = df[df['time_dt'] < df['time_dt'].min() + timedelta(minutes=10)]
    df['lambda_over_n'] = df['rps'] / df['ready_count']
    df['current_cc'] = df['total_conc'] / df['ready_count']
    # set index to the time
    df = df.set_index('time_dt')
    return df
