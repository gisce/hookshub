from os.path import abspath, normpath, dirname, join
from json import loads
from listener import HookListener
from expects import *
from mock import patch, Mock

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)              # Project Directory
data_path = join(project_path, 'test_data')  # Test Directory

with description('Hook Listener'):
    with context('Webhook test data'):
        with it('must return a hook with "webhook" origin on instancer method'):
            webhook_data_path = join(
                data_path, join('webhook', 'default_event')
            )
            webhook_data = loads(open(webhook_data_path, 'r').read())
            hook = HookListener.instancer(webhook_data)
            expect(hook.origin).to(equal('webhook'))

        with context('running actions correctly (mocked)'):
            with it('must run successfully all actions'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                listener = HookListener(webhook_data_path, 'default_event')
                with patch("listener.Popen") as popen:
                    popen.start()
                    popen_mock = Mock()
                    popen_mock.communicate.return_value = ['All Ok\n', '']
                    popen_mock.returncode = 0
                    popen.return_value = popen_mock
                    result, log = listener.run_event_actions()
                    expect(result).to(equal(0))
                    popen.stop()

        with context('running actions wrongly (mocked)'):
            with it('must run failing all actions'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                listener = HookListener(webhook_data_path, 'default_event')
                with patch("listener.Popen") as popen:
                    popen.start()
                    popen_mock = Mock()
                    popen_mock.communicate.return_value = ['', 'All bad\n']
                    popen_mock.returncode = -1
                    popen.return_value = popen_mock
                    result, log = listener.run_event_actions()
                    expect(result).to(equal(-1))
                    popen.stop()

    with context('GitLab test data'):
        with it('must return a hook with "GitLab" origin on instancer method'):
            webhook_data_path = join(data_path, join('gitlab', 'issue.json'))
            webhook_data = loads(open(webhook_data_path, 'r').read())
            hook = HookListener.instancer(webhook_data)
            expect(hook.origin).to(equal('gitlab'))

    with context('GitHub test data'):
        with it('must return a hook with "GitHub" origin on instancer method'):
            webhook_data_path = join(data_path, join('github', 'status.json'))
            webhook_data = loads(open(webhook_data_path, 'r').read())
            hook = HookListener.instancer(webhook_data)
            expect(hook.origin).to(equal('github'))
