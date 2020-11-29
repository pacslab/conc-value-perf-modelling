import asyncio
import time
import socketio

# to allow nested execution of asyncio functions
import nest_asyncio
nest_asyncio.apply()

import threading
import uuid
import os

# system characteristics
client_uuid = str(uuid.uuid4())
# experiment name
experiment_name = os.getenv('EXPERIMENT_NAME', 'DEFAULT_EXPERIMENT')

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

def start_thread():
    # we make it a daemon thread to die when the main thread exits
    t = threading.Thread(target=asyncio_thread, args=(), daemon=True)
    t.start()

if __name__ == '__main__':
    import time

    # register signal handlers
    register_signal_handlers()

    # start asyncio thread
    start_thread()

    # wait forever (in this file we can just wait for the thread)
    while True:
        time.sleep(0.1)
