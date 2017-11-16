from __future__ import print_function
from multiprocessing import Pool
from copy_reg import pickle
from types import MethodType
import logging
import signal

from json import loads, dumps
from tempfile import mkstemp
from sys import argv
from os import remove, fdopen
from os.path import abspath, normpath, dirname, join

from flask import Flask, request, abort, jsonify
from hookshub.parser import HookParser
from raven.contrib.flask import Sentry


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

pickle(MethodType, _pickle_method)

DEFAULT_IP = '0.0.0.0'
DEFAULT_PORT = 5000
DEFAULT_PROCS = 4


class AbortException(Exception):
    def __init__(self, msg):
        '''
        Override Exception so we can return our own message to the request as
        an error response.
        :param msg: Message to print on the response
        '''
        msg = 'Internal Server Error\n{}'.format(msg)
        self.message = msg
        self.code = 500


def close_worker(signum, frame):
    from os import getpid
    from signal import SIGTERM, SIGINT, SIGQUIT
    sig = 'TERM' if signum == SIGTERM else (
        'INT' if signum == SIGINT else (
            'QUIT' if signum == SIGQUIT else 'UNKNOWN'
        )
    )
    log = logging.getLogger(__name__)
    log.warning('Stopping worker {} with: SIG{}'.format(
        getpid(), sig
    ))
    return SIGQUIT


def init_worker():
    '''
    This method initializes the workers from the action pool.
    Basically this makes SIGINT to be 'ignored' so it can be catched in the
    parent process.
    '''
    signal.signal(signal.SIGTERM, close_worker)
    signal.signal(signal.SIGINT, close_worker)
    signal.signal(signal.SIGQUIT, close_worker)


def get_args():
    '''
    Parse arguments from sys.argv. Expected Arguments are:
    --ip=<ip_address>       -   Specify ip address to bind and listen
    --port=<port_num>       -   Specify port num to bind and listen
    --procs=<process_num>   -   Number of processes to spawn and run actions
    --help                  -   Show Usage and close
    :return: Useful params always as a tuple (ip, port number, process number)
    '''
    host_ip = DEFAULT_IP
    host_port = DEFAULT_PORT
    proc_num = DEFAULT_PROCS
    if len(argv) > 1:
        log = logging.getLogger(__name__)
        for arg in argv:
            if arg.startswith('--ip='):
                host_ip = arg[5::]
            elif arg.startswith('--port='):
                host_port = int(arg[7::])
            elif arg.startswith('--procs='):
                proc_num = int(arg[8::])
            elif arg.startswith('--help'):
                out = 'Usage:\npython listener.py [options]'
                out += '\n\t[--ip=<ip_address>]\t\t\t- sets listening address'
                out += '\n\t[--port=<port_number>]\t\t- sets listening port'
                out += '\n\t[--procs=<process_number>]\t- sets the number of' \
                       ' processes to start running actions'
                log.error(
                    out
                )
                exit(0)
            elif not arg.endswith('listener.py'):
                log.error(
                    'Got unrecognized argument: [{}]'.format(arg)
                )
        return host_ip, host_port, proc_num
    return host_ip, host_port, proc_num


application = Flask(__name__)


@application.errorhandler(AbortException)
def handle_abort(e):
    '''
    Return handled exception as an error page from AbortException
    :param e: Exception - May contain information generated from AbortException
    :return: HTTP Response to return by the WSGI server
    '''
    response = jsonify(e.message)
    response.content_type = 'text/html'
    response.status_code = e.code
    return response


@application.route('/', methods=['POST'])
def index():
    """
    Main WSGI application entry.
    """
    path = normpath(abspath(dirname(__file__)))

    # Load config
    global config
    if 'config' not in globals():
        with open(join(path, 'config.json'), 'r') as cfg:
            config = loads(cfg.read())

    # Get Event // Implement ping
    event = request.headers.get(
        'X-GitHub-Event', request.headers.get(
            'X-GitLab-Event', 'ping'
        )
    )
    if event == 'ping':
        return dumps({'msg': 'pong'})

    # Gather data
    try:
        payload = loads(request.data)
    except:
        abort(400)

    # Save payload to temporal file
    osfd, tmpfile = mkstemp()
    with fdopen(osfd, 'w') as pf:
        pf.write(dumps(payload))

    # Use HooksHub to run actions
    global pool
    if not ('pool' in globals()):
        pool = None
    parser = HookParser(tmpfile, event, pool)

    log_out = ('Processing: {}...'.format(parser.event))

    code, output = parser.run_event_actions(config)
    output = '{0}|{1}'.format(log_out, output)
    if code:  # Error executing actions
        output = 'Fail with {}\n{}'.format(event, output)
    else:  # All ok
        output = 'Success with {}\n{}'.format(event, output)

    code_hooks, output_hooks = parser.run_event_hooks(config)

    # Remove temporal file
    remove(tmpfile)

    output_hooks = '{0}|{1}'.format(log_out, output_hooks)
    if code_hooks:  # Error executing actions
        output = '{}\nFail with {}\n{}'.format(
            output, event, output_hooks)
    else:  # All ok
        output = '{}\nSuccess with {}\n{}'.format(
            output, event, output_hooks)
    if code or code_hooks:
        raise AbortException(output)
    return dumps({'msg': output})


def start_listening(host_ip=DEFAULT_IP,
                    host_port=DEFAULT_PORT,
                    proc_num=DEFAULT_PROCS):
    global config
    from os.path import isfile
    path = normpath(abspath(dirname(__file__)))
    config_path = join(path, 'config.json')
    if isfile(config_path):
        with open(config_path, 'r') as cfg:
            config = loads(cfg.read())
    else:
        config = {}
    sentry = Sentry(application)
    logging.getLogger(__name__).info(
        'Start Listening on {}:{} with {} procs'.format(
            host_ip, host_port, proc_num
        )
    )
    global pool
    pool = Pool(processes=proc_num, initializer=init_worker)
    try:
        application.run(debug=False, host=host_ip, port=host_port)
    finally:
        pool.terminate()
        pool.close()


logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='[%Y/%m/%d-%H:%M:%S]',
                    level=logging.INFO)

if __name__ == '__main__':
    host_ip, host_port, proc_num = get_args()
    start_listening(host_ip, host_port, proc_num)
