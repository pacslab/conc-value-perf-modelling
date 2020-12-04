import asyncio
import time
import socketio

# to allow nested execution of asyncio functions
import nest_asyncio
nest_asyncio.apply()

import threading
import uuid
import os
# for deep copy of objects
# import copy
from collections import OrderedDict

# system characteristics
client_uuid = str(uuid.uuid4())
# experiment name
experiment_name = os.getenv('EXPERIMENT_NAME', 'DEFAULT_EXPERIMENT')
report_interval = os.getenv('REPORT_INTERVAL', '10')
report_interval = float(report_interval)

loop = asyncio.get_event_loop()
sio = socketio.AsyncClient()
start_timer = None

def register_signal_handlers():
    # signal handling imports
    import signal
    import sys

    # add signal handling logic
    def handler_stop_signals(signum, frame):
        # handle stop signal
        print('Received SIGTERM or SIGINT, stopping service...')
        loop.run_until_complete(disc_client_info())
        # wait for the information to be sent
        time.sleep(0.2)
        sys.exit(0)

    # Handle SIGINT
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

def get_client_info():
    return {
        'client_uuid': client_uuid,
        'experiment_name': experiment_name,
    }

async def conn_client_info():
    await sio.emit('conn_client_info', get_client_info())

async def disc_client_info():
    await sio.emit('disc_client_info', get_client_info())

async def send_routine_report(report):
    await sio.emit('routine_report', report)

@sio.event
async def connect():
    print('connected to server')
    await conn_client_info()


@sio.event
async def pong_from_server():
    global start_timer
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    await sio.sleep(1)


async def start_server():
    await sio.connect('http://172.17.0.1:3000')
    while True:
        await sio.sleep(0.1)

def asyncio_thread():
    loop.run_until_complete(start_server())

# concurrency value logging variables
from collections import namedtuple

conc_value_lock = threading.Lock()
conc_hist_lock = threading.Lock()
service_time_lock = threading.Lock()
curr_conc_value = 0
last_conc_transition = time.time()

# history of concurrency value through time
ConcHist = namedtuple('ConcHist', ['time', 'conc_value'])
conc_hist = []
# history of service time through time
service_time_hist = dict()

# log concurrency value
def logConcurrencyValue():
    return print(f"Concurrency value: {curr_conc_value}")

def prepareNewConcValue():
    global last_conc_transition
    with conc_hist_lock:
        new_conc_time = time.time()
        # the time we were in previous conc value
        prev_conc_time = new_conc_time - last_conc_transition
        h = ConcHist(prev_conc_time, curr_conc_value)
        conc_hist.append(h)
        last_conc_transition = new_conc_time

# called when a new request arrived
def requestArrival():
    prepareNewConcValue()
    global curr_conc_value
    with conc_value_lock:
        curr_conc_value += 1
    # logConcurrencyValue()

# called when request about to depart
def requestDeparture(resp_time):
    prepareNewConcValue()
    global curr_conc_value
    with conc_value_lock:
        curr_conc_value -= 1
    # logConcurrencyValue()
    with service_time_lock:
        resp_time = round(resp_time * 1000 / 50) * 50
        if resp_time in service_time_hist:
            service_time_hist[resp_time] += 1
        else:
            service_time_hist[resp_time] = 1


def calculateConcHistogram():
    # add current value to history
    prepareNewConcValue()

    # calculate histogram
    with conc_hist_lock:
        conc_histogram = dict()
        for h in conc_hist:
            if h.conc_value in conc_histogram:
                conc_histogram[h.conc_value] += h.time
            else:
                conc_histogram[h.conc_value] = h.time

        # clear history
        conc_hist.clear()

    # sort the keys before sending them
    od = OrderedDict(sorted(conc_histogram.items()))

    return {
        'conc_values': list(od.keys()),
        'conc_times': list(od.values()),
    }

def calculateServiceTimeHistogram():
    with service_time_lock:
        # deep copy the object
        # service_time_hist_copy = copy.deepcopy(service_time_hist)

        # sort the keys before sending them
        od = OrderedDict(sorted(service_time_hist.items()))
        
        service_time_hist_copy = {
            'service_time_values': list(od.keys()),
            'service_time_times': list(od.values()),
        }

        # clear history
        service_time_hist.clear()

    return service_time_hist_copy
    

def sendReports():
    print('Sending report...')
    # first, calculate histogram
    conc_histogram = calculateConcHistogram()
    service_histogram = calculateServiceTimeHistogram()
    # next, send report
    report = {
        'client_info': get_client_info(),
        'conc_histogram': conc_histogram,
        'service_time_hist': service_histogram,
    }
    loop.run_until_complete(send_routine_report(report))

def generateScheduledReports():
    time.sleep(report_interval)
    while True:
        lastReportSent = time.time()
        sendReports()
        wait_time = report_interval - (time.time() - lastReportSent)
        if wait_time > 0:
            time.sleep(wait_time)



def start_thread():
    # we make it a daemon thread to die when the main thread exits
    t1 = threading.Thread(target=asyncio_thread, args=(), daemon=True)
    t2 = threading.Thread(target=generateScheduledReports, args=(), daemon=True)
    t1.start()
    t2.start()

if __name__ == '__main__':
    import time

    # register signal handlers
    register_signal_handlers()

    # start asyncio thread
    start_thread()

    # wait forever (in this file we can just wait for the thread)
    while True:
        time.sleep(0.1)
