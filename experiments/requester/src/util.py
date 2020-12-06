
import os
import sys

import requests

logger_path = os.getenv('LOGGER_PATH')
exp_name = os.getenv('EXP_NAME')

if logger_path is None:
    print("LOGGER_PATH environment variable is necessary!")
    sys.exit(1)
if exp_name is None:
    print("EXP_NAME environment variable is necessary!")
    sys.exit(1)

print("Loaded logger path:", logger_path)
print("Loaded experiment name:", exp_name)

def clear_logger():
    print('clearing the logger...')
    clear_path = f"{logger_path}/logger/clear"
    print(clear_path)
    res = requests.get(clear_path)
    print(f'result [{res.status_code}]: {res.text}')
    print('clearning done')

