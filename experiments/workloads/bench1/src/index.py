import signal

run = True

def handler_stop_signals(signum, frame):
    global run

    # handle stop signal
    print('Received SIGTERM or SIGINT, stopping service...')

    run = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

while run:
    pass # do stuff including other IO stuff

