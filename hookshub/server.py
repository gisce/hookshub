from __future__ import print_function
from multiprocessing import Pool

import logging

from json import loads, dumps
from tempfile import mkstemp
from os import remove, fdopen
from os.path import abspath, normpath, dirname, join

from flask import Flask, request, abort, jsonify
from hookshub.listener import HookListener


class AbortException(Exception):
    def __init__(self, msg):
        msg = 'Internal Server Error\n{}'.format(msg)
        self.message = msg
        self.code = 500

application = Flask(__name__)


@application.errorhandler(AbortException)
def handle_abort(e):
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
    with open(join(path, 'config.json'), 'r') as cfg:
        config = loads(cfg.read())

    hooks = config.get('hooks_path', join(path, 'hooks'))

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
    listener = HookListener(tmpfile, event, pool)

    log_out = ('Processing: {}...'.format(listener.event))

    code, output = listener.run_event_actions(config)

    output = '{0}|{1}'.format(log_out, output)
    # Remove temporal file
    remove(tmpfile)

    if code != 0:  # Error executing actions
        output = 'Fail with {}\n{}'.format(event, output)
        raise AbortException(output)
    else:  # All ok
        output = 'Success with {}\n{}'.format(event, output)
    return dumps({'msg': output})


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='[%Y/%m/%d-%H:%M:%S]')
    pool = Pool(processes=4)
    application.run(debug=False, host='0.0.0.0')
