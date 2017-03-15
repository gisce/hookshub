from mock import patch, Mock
from expects import *

with patch('hookshub.listener.Pool') as pool:
    with patch('hookshub.listener.Flask') as flask:
        pool.start()
        proc_pool = Mock()
        proc_pool.terminate.return_value = True
        pool.return_value = proc_pool
        flask.start()
        app_mock = Mock()
        app_mock.run = True
        from hookshub import listener

        with description('Listener Methods'):
            with context("With Workers' init and close methods"):
                with it('Must not close the worker and return SIGQUIT signal'):
                    import signal
                    signal_given = signal.SIGINT
                    signal_returned = listener.close_worker(
                        signum=signal_given, frame=None
                    )
                    expect(signal_returned).to(equal(signal.SIGQUIT))

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
                        expect(listener.get_args()).to(equal((
                            given_ip,
                            int(given_port),
                            int(given_procs)
                        )))

        flask.stop()
    pool.stop()


