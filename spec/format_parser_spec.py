from os.path import abspath, normpath, dirname, join
from json import loads
from hookshub.parser import HookParser
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
            hook = HookParser.instancer(webhook_data)
            expect(hook.origin).to(equal('webhook'))

        with context('running actions correctly (mocked)'):
            with it('must run successfully all actions'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                parser = HookParser(webhook_data_path, 'default_event')
                config = join(
                    data_path, join('webhook', 'conf.json')
                )
                with patch("hookshub.parser.Pool") as pool:
                    action_return = ['All Ok\n', '', 0, 0]
                    pool.start()
                    apply_async = Mock()
                    apply_async.wait.return_value = True
                    apply_async.ready.return_value = True
                    apply_async.get.return_value = action_return
                    pool.apply_async.return_value = apply_async
                    parser.pool = pool
                    result, log = parser.run_event_actions(config)
                    expect(result).to(equal(0))
                    pool.stop()

        with context('running actions wrongly (mocked)'):
            with it('must run failing all actions'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                parser = HookParser(webhook_data_path, 'default_event')
                config = join(
                    data_path, join('webhook', 'conf.json')
                )
                with patch("hookshub.parser.Pool") as pool:
                    action_return = ['All Bad\n', '', -1, 0]
                    pool.start()
                    apply_async = Mock()
                    apply_async.wait.return_value = True
                    apply_async.ready.return_value = True
                    apply_async.get.return_value = action_return
                    pool.apply_async.return_value = apply_async
                    parser.pool = pool
                    result, log = parser.run_event_actions(config)
                    expect(result).to(equal(-1))
                    pool.stop()

        with context('running actions delayed (mocked)'):
            with it('must run async the actions and log it'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                parser = HookParser(webhook_data_path, 'default_event')
                config = join(
                    data_path, join('webhook', 'conf.json')
                )
                with patch("hookshub.parser.Pool") as pool:
                    action_return = ['All Ok\n', '', 0, 0]
                    pool.start()
                    apply_async = Mock()
                    apply_async.wait.return_value = True
                    apply_async.ready.return_value = False
                    pool.apply_async.return_value = apply_async
                    parser.pool = pool
                    result, log = parser.run_event_actions(config)
                    expect(result).to(equal(0))
                    pool.stop()

    with context('Run Actions (mocked), called from subprocess in production.'):
        with it('must run successfully the action'):
            from hookshub.parser import run_action
            webhook_data_path = join(
                data_path, join('webhook', 'default_event')
            )
            parser = HookParser(webhook_data_path, 'default_event')
            hook = parser.instancer(parser.payload)
            config = join(
                data_path, join('webhook', 'conf.json')
            )
            with patch("hookshub.parser.Popen") as popen:
                res_out = 'All Ok\n'
                res_err = ''
                res_code = 0
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = [res_out, res_err]
                popen_mock.returncode = res_code
                popen.return_value = popen_mock
                stdout, stderr, returncode, pid = run_action(
                    parser.event, hook, config
                )
                expect(stdout).to(equal(res_out))
                expect(stderr).to(equal(res_err))
                expect(returncode).to(equal(res_code))
                popen.stop()

    with context('Run Actions (mocked), called from subprocess in production.'):
        with it('must fail running the action'):
            from hookshub.parser import run_action

            webhook_data_path = join(
                data_path, join('webhook', 'default_event')
            )
            parser = HookParser(webhook_data_path, 'default_event')
            hook = parser.instancer(parser.payload)
            config = join(
                data_path, join('webhook', 'conf.json')
            )
            with patch("hookshub.parser.Popen") as popen:
                res_out = 'All Ok\n'
                res_err = ''
                res_code = -1
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = [res_out, res_err]
                popen_mock.returncode = res_code
                popen.return_value = popen_mock
                stdout, stderr, returncode, pid = run_action(
                    parser.event, hook, config
                )
                expect(stdout).to(equal(res_out))
                expect(stderr).to(equal(res_err))
                expect(returncode).to(equal(res_code))
                popen.stop()

    with context('GitLab test data'):
        with it('must return a hook with "GitLab" origin on instancer method'):
            webhook_data_path = join(data_path, join('gitlab', 'issue.json'))
            webhook_data = loads(open(webhook_data_path, 'r').read())
            hook = HookParser.instancer(webhook_data)
            expect(hook.origin).to(equal('gitlab'))

    with context('GitHub test data'):
        with it('must return a hook with "GitHub" origin on instancer method'):
            webhook_data_path = join(data_path, join('github', 'status.json'))
            webhook_data = loads(open(webhook_data_path, 'r').read())
            hook = HookParser.instancer(webhook_data)
            expect(hook.origin).to(equal('github'))
