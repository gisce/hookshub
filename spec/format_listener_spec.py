from mock import patch, Mock
from expects import *
from hookshub import listener

# These Test must execute before mocks on listner!
#   Just leave the tests in this description in top of the file :D
with description('Application Requests'):
    with context('On Sample Hook'):
        with it('Must make a simple response (act as PONG from PING request)'):
            from os.path import abspath, normpath, dirname, join
            from json import loads

            my_path = normpath(abspath(dirname(__file__)))
            project_path = dirname(my_path)  # Project Directory
            app = listener.application
            global client
            client = app.test_client()
            hook_headers = None

            response = client.post('/', headers=hook_headers)
            data = loads(response.data)
            expected_data = {
                'msg': 'pong'
            }
            expect(expected_data).to(equal(data))

        with it('Must make a response with hook parser message'):
            from os.path import abspath, normpath, dirname, join
            from json import loads, dumps

            my_path = normpath(abspath(dirname(__file__)))
            project_path = dirname(my_path)  # Project Directory

            data_path = join(project_path, 'test_data', 'github', 'gollum.json')
            with open(data_path, 'r') as f:
                hook_data = dumps(loads(f.read()))
            hook_headers = {
                'X-GitHub-Event': True,
                'Content-Length': len(hook_data)
            }
            hook_headers = loads(dumps(hook_headers))
            global client

            with patch('hookshub.listener.HookParser') as HookParser:
                HookParser.start()
                parser = Mock()
                parser.event.return_value = 'Mocked Event'
                parser.run_event_actions.return_value = (0, 'All OK')
                parser.run_event_hooks.return_value = (0, 'All OK')
                HookParser.return_value = parser

                response = client.post(
                    '/', data=hook_data, headers=hook_headers
                )
                ping_data = {
                    'msg': 'pong'
                }
                data = loads(response.data)
                expect(response.status_code).to(equal(200))
                expect(data).not_to(equal(ping_data))
                HookParser.stop()

        with it('Must make an abort response with hook parser message'):
            from os.path import abspath, normpath, dirname, join
            from json import loads, dumps

            my_path = normpath(abspath(dirname(__file__)))
            project_path = dirname(my_path)  # Project Directory

            data_path = join(project_path, 'test_data', 'github', 'gollum.json')
            with open(data_path, 'r') as f:
                hook_data = dumps(loads(f.read()))
            hook_headers = {
                'X-GitHub-Event': True,
                'Content-Length': len(hook_data)
            }
            hook_headers = loads(dumps(hook_headers))
            global client

            with patch('hookshub.listener.HookParser') as HookParser:
                HookParser.start()
                parser = Mock()
                parser.event.return_value = 'Mocked Event'
                parser.run_event_actions.return_value = (-1, 'All Bad')
                parser.run_event_hooks.return_value = (-1, 'All Bad')
                HookParser.return_value = parser

                response = client.post('/', data=hook_data,
                                       headers=hook_headers)
                ping_data = {
                    'msg': 'pong'
                }
                data = loads(response.data)
                expect(response.status_code).to(equal(500))
                expect(data).not_to(equal(ping_data))

                HookParser.stop()

        with it('Must make an abort response with bad hook data'):
            from os.path import abspath, normpath, dirname, join
            from json import loads, dumps

            my_path = normpath(abspath(dirname(__file__)))
            project_path = dirname(my_path)  # Project Directory

            data_path = join(
                project_path, 'test_data', 'github', 'bad_push.json'
            )
            with open(data_path, 'r') as f:
                hook_data = dumps(loads(f.read()))
            hook_headers = {
                'X-GitHub-Event': True,
                'Content-Length': len(hook_data)
            }
            hook_headers = loads(dumps(hook_headers))
            global client
            with patch('hookshub.listener.loads') as load:
                load.side_effect = Exception('Mocked Bad JSON Data')
                response = client.post('/', data=hook_data,
                                           headers=hook_headers)
                ping_data = {
                    'msg': 'pong'
                }
                expect(response.status_code).to(equal(400))


with description('Listener Methods'):
    with context("With Workers' init and close methods"):
        with it('Must not close the worker and return SIGQUIT signal'):
            import signal
            with patch('hookshub.listener.logging') as logging:
                logging.start()
                logging.basicConfig.return_value = True
                logging.info = True
                logger = Mock()
                logger.info.return_value = True
                logger.error.return_value = True
                logging.getLogger.return_value = logger
                signal_given = signal.SIGINT
                signal_returned = listener.close_worker(
                    signum=signal_given, frame=None
                )
                expect(signal_returned).to(equal(signal.SIGQUIT))
                logging.stop()

        with it('Must replace killing signals with close method'):
            with patch('hookshub.listener.signal') as signal_mock:
                signal_mock.start()
                signal_mock.signal.return_code = True
                listener.init_worker()
                signal_mock.stop()

    with context('Given a list of arguments'):
        with it('Must return default host_ip, host_port and proc_num'
                'Given 0 arguments'):
            args = ['listener.py']
            with patch.object(listener, 'argv', args) as argv:
                expect(listener.get_args()).to(equal((
                    listener.DEFAULT_IP,
                    listener.DEFAULT_PORT,
                    listener.DEFAULT_PROCS
                )))

        with it('Must return given args as host_ip, host_port and'
                'proc_num; Also Must Ignore incorrect params'):
            given_ip = '1.2.3.4'
            given_port = '1234'
            given_procs = '12'
            args = [
                'listener.py',
                '--ip={}'.format(given_ip),
                '--port={}'.format(given_port),
                '--ports=1234,2341',
                '--procs={}'.format(given_procs)
            ]
            with patch.object(listener, 'argv', args) as argv:
                with patch('hookshub.listener.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    expect(listener.get_args()).to(equal((
                        given_ip,
                        int(given_port),
                        int(given_procs)
                    )))

                    logging.stop()

        with it('Must log usage and quit with --help'):
            args = [
                'listener.py',
                '--ports=1234,2341',
                '--help'
            ]
            with patch.object(listener, 'argv', args) as argv:
                with patch('hookshub.listener.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    exited = False
                    try:
                        listener.get_args()
                    except SystemExit:
                        exited = True
                    expect(exited).to(equal(True))

                    logging.stop()

    with context('On Application Starting'):
        with it('Must start (mocked) with the specified args'):
            with patch('hookshub.listener.Pool') as pool:
                pool.start()
                proc_pool = Mock()
                proc_pool.terminate.return_value = True
                pool.return_value = proc_pool
                with patch('hookshub.listener.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    with patch('hookshub.listener.Sentry') as sentry:
                        sentry.start()
                        sentry.return_value = True

                        app_mock = Mock()
                        app_mock.run.return_value = True
                        listener.application = app_mock
                        listener.start_listening('1.2.3.4', 1234, 2)

                        sentry.stop()
                    logging.stop()
                pool.stop()

        with it('Must start (mocked) with the default args'):
            with patch('hookshub.listener.Pool') as pool:
                pool.start()
                proc_pool = Mock()
                proc_pool.terminate.return_value = True
                pool.return_value = proc_pool
                with patch('hookshub.listener.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger
                    with patch('hookshub.listener.Sentry') as sentry:
                        sentry.start()
                        sentry.return_value = True

                        app_mock = Mock()
                        app_mock.run.return_value = True
                        listener.application = app_mock
                        listener.start_listening()

                        sentry.stop()
                    logging.stop()
                pool.stop()
