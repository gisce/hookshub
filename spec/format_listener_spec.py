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

            

        flask.stop()
    pool.stop()


