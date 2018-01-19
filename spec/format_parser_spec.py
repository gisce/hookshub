from os.path import abspath, normpath, dirname, join
from json import loads
from hookshub.parser import HookParser
from expects import *
from mamba import *
from mock import patch, Mock

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)              # Project Directory
data_path = join(project_path, 'test_data')  # Test Directory

with description('Hook Parser'):
    with it('must use context manager and remove the payload file on exit'):
        from os.path import join, isfile
        from hookshub.parser import TempDir
        with TempDir() as tmpdir:
            filepath = join(tmpdir.dir, 'test_file')
            with open(filepath, 'w') as tmp_data:
                with open(join(
                        data_path, join('webhook', 'default_event')
                ), 'r') as hook_data_path:
                    tmp_data.write(hook_data_path.read())
            with HookParser(filepath, 'default_event') as p:
                pass
            expect(isfile(filepath)).to(be_false)

    with context('No data for hooks'):
        with it('must run no hooks or actions'):
            fake_datapath = join(
                    data_path, join('webhook', 'fake_event')
                )
            config_file = join(data_path, 'webhook', 'conf.json')
            with open(config_file, 'r') as conf:
                config = loads(conf.read())
            parser = HookParser(fake_datapath, 'fake_event')
            expect(parser.hook.event).to(equal('fake_event'))
            expect(parser.event).to(equal('fake_event'))
            parser.run_event_hooks(config)
            parser.run_event_actions(config)

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
                config_file = join(data_path, 'webhook', 'conf.json')
                with open(config_file, 'r') as conf:
                    config = loads(conf.read())
                with patch("hookshub.parser.Pool") as pool:
                    pool.start()
                    action_return = ('All Ok\n', '', 0, 0)
                    apply_async = Mock()
                    apply_async.wait.return_value = True
                    apply_async.ready.return_value = True
                    apply_async.get.return_value = action_return
                    pool_mock = Mock()
                    pool_mock.apply_async.return_value = apply_async
                    pool.return_value = pool_mock
                    with patch('hookshub.parser.logging') as logging:
                        logging.start()
                        logging.basicConfig.return_value = True
                        logging.info = True
                        logger = Mock()
                        logger.info.return_value = True
                        logger.error.return_value = True
                        logging.getLogger.return_value = logger

                        parser = HookParser(
                            payload_file=webhook_data_path,
                            event='default_event',
                            procs=0)
                        parser.logger = logger
                        result, log = parser.run_event_actions(config)
                        expect(result).to(equal(0))
                        logging.stop()
                    pool.stop()

        with context('running actions wrongly (mocked)'):
            with it('must run failing all actions'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                config_file = join(data_path, 'webhook', 'conf.json')
                with open(config_file, 'r') as conf:
                    config = loads(conf.read())
                with patch('hookshub.parser.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    with patch("hookshub.parser.Pool") as pool:
                        parser = HookParser(webhook_data_path, 'default_event')
                        parser.logger = logger
                        action_return = ('All Bad\n', '', -1, 0)
                        apply_async = Mock()
                        apply_async.wait.return_value = True
                        apply_async.ready.return_value = True
                        apply_async.get.return_value = action_return
                        pool_mock = Mock()
                        pool_mock.apply_async.return_value = apply_async
                        pool.return_value = pool_mock
                        parser.pool = pool
                        result, log = parser.run_event_actions(config)
                        expect(result).to(equal(-1))

                        logging.stop()
                    pool.stop()

        with context('running actions delayed (mocked)'):
            with it('must run async the actions and log it'):
                webhook_data_path = join(
                    data_path, join('webhook', 'default_event')
                )
                config_file = join(data_path, 'webhook', 'conf.json')
                with open(config_file, 'r') as conf:
                    config = loads(conf.read())
                with patch('hookshub.parser.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    with patch("hookshub.parser.Pool") as pool:

                        parser = HookParser(webhook_data_path, 'default_event')
                        parser.logger = logger
                        action_return = ('All Ok\n', '', 0, 0)
                        apply_async = Mock()
                        apply_async.wait.return_value = True
                        apply_async.ready.return_value = True
                        apply_async.get.return_value = action_return
                        pool_mock = Mock()
                        pool_mock.apply_async.return_value = apply_async
                        pool.return_value = pool_mock
                        result, log = parser.run_event_actions(config)
                        expect(result).to(equal(0))
                        logging.stop()
                    pool.stop()

    with context('Run Actions (mocked), called from subprocess in production.'):
        with it('must run successfully the action'):
            from hookshub.parser import run_action
            webhook_data_path = join(
                data_path, join('webhook', 'default_event')
            )
            config = join(
                data_path, join('webhook', 'conf.json')
            )
            with patch("hookshub.parser.Popen") as popen:
                with patch('hookshub.parser.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    parser = HookParser(webhook_data_path, 'default_event')
                    parser.logger = logger
                    hook = parser.instancer(parser.payload)
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
                    logging.stop()
                popen.stop()

        with it('must fail running the action'):
            from hookshub.parser import run_action

            webhook_data_path = join(
                data_path, join('webhook', 'default_event')
            )
            config = join(
                data_path, join('webhook', 'conf.json')
            )
            with patch("hookshub.parser.Popen") as popen:
                with patch('hookshub.parser.logging') as logging:
                    logging.start()
                    logging.basicConfig.return_value = True
                    logging.info = True
                    logger = Mock()
                    logger.info.return_value = True
                    logger.error.return_value = True
                    logging.getLogger.return_value = logger

                    parser = HookParser(webhook_data_path, 'default_event')
                    parser.logger = logger
                    hook = parser.instancer(parser.payload)
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
                    logging.stop()
                popen.stop()

    with context('Log Result (mocked), called async after timeout.'):
        with it('must log result for event action'):
            with patch('hookshub.parser.logging') as logging:
                logging.start()
                logging.basicConfig.return_value = True
                logging.info = True
                logger = Mock()
                logger.info.return_value = True
                logger.error.return_value = True
                logging.getLogger.return_value = logger
                from hookshub.parser import log_result

                res_out = 'All Ok\n'
                res_err = ''
                res_pid = res_code = 0
                res = (res_out, res_err, res_code, res_pid)
                log_result(res)
                res_code = -1
                res = (res_out, res_err, res_code, res_pid)
                log_result(res)

                logging.stop

        with it('must log result for hook action'):
            with patch('hookshub.parser.logging') as logging:
                logging.start()
                logging.basicConfig.return_value = True
                logging.info = True
                logger = Mock()
                logger.info.return_value = True
                logger.error.return_value = True
                logging.getLogger.return_value = logger
                from hookshub.parser import log_hook_result

                hook_name = 'MOCK'
                res_code = 0
                res = (res_code, hook_name)
                log_hook_result(res)
                res_code = -1
                res = (res_code, hook_name)
                log_hook_result(res)

                logging.stop()

    with context('Load Hooks (Plugins):'):
        with it('must get a list of hooks from HooksManager'):
            with patch('hookshub.hook.get_hooks') as get_hook_mock:
                get_hook_mock.start()
                get_hook_list = [('hook_name', 'hook_used')]
                get_hook_mock.return_value = get_hook_list
                hook_list = HookParser.load_hooks(event='None',
                                                  repository='None',
                                                  branch='None')
                expect(hook_list).to(equal(get_hook_list))
                get_hook_mock.stop()

    with context('Run Hooks (mocked), called from subprocess in production.'):
        with it('must timeout running all hooks'):
            with patch('hookshub.hook.get_hooks') as get_hook_mock:
                with patch('hookshub.parser.logging') as logging:
                    with patch('hookshub.parser.Pool') as pooler:
                        webhook_data_path = join(
                            data_path, join('webhook', 'default_event')
                        )
                        default_conf = {
                            'github_token': 'GHT',
                            'gitlab_token': 'GLT',
                            'vhost_path': 'VHP'
                        }
                        proc = Mock()
                        proc.wait.return_value = True
                        proc.ready.return_value = False

                        pool = Mock()
                        pool.apply_async.return_value = proc

                        pooler.start()
                        pooler.return_value = pool

                        logging.start()
                        logging.basicConfig.return_value = True
                        logging.info = True
                        logger = Mock()
                        logger.info.return_value = True
                        logger.error.return_value = True
                        logging.getLogger.return_value = logger

                        hook_used = Mock()
                        hook_used.get_args.return_value = {}
                        hook_used.run_hook = lambda *a: True

                        get_hook_mock.start()
                        get_hook_list = [('hook_name', hook_used)]
                        get_hook_mock.return_value = get_hook_list

                        parser = HookParser(webhook_data_path,
                                            event='default_event',
                                            procs=1)
                        res = parser.run_event_hooks(def_conf=default_conf)
                        expected_code = 0
                        expected_log = '[hook_name]:Success!\n'
                        expect(res).to(equal((expected_code, expected_log)))

        with it('must run successfully all hooks'):
            with patch('hookshub.hook.get_hooks') as get_hook_mock:
                with patch('hookshub.parser.logging') as logging:
                    with patch('hookshub.parser.Pool') as pooler:
                        webhook_data_path = join(
                            data_path, join('webhook', 'default_event')
                        )
                        default_conf = {
                            'github_token': 'GHT',
                            'gitlab_token': 'GLT',
                            'vhost_path': 'VHP'
                        }
                        proc = Mock()
                        proc.wait.return_value = True
                        proc.ready.return_value = True
                        proc.get.return_value = (0, 'success_hook')

                        pool = Mock()
                        pool.apply_async.return_value = proc

                        pooler.start()
                        pooler.return_value = pool

                        logging.start()
                        logging.basicConfig.return_value = True
                        logging.info = True
                        logger = Mock()
                        logger.info.return_value = True
                        logger.error.return_value = True
                        logging.getLogger.return_value = logger

                        hook_used = Mock()
                        hook_used.get_args.return_value = {}
                        hook_used.run_hook = lambda *a: True

                        get_hook_mock.start()
                        get_hook_list = [('hook_name', hook_used)]
                        get_hook_mock.return_value = get_hook_list

                        parser = HookParser(webhook_data_path,
                                            event='default_event',
                                            procs=1)
                        res = parser.run_event_hooks(def_conf=default_conf)
                        expected_code = 0
                        expected_log = '[hook_name]:Success!\n'
                        expect(res).to(equal((expected_code, expected_log)))

        with it('must fail running all hooks'):
            with patch('hookshub.hook.get_hooks') as get_hook_mock:
                with patch('hookshub.parser.logging') as logging:
                    with patch('hookshub.parser.Pool') as pooler:
                        webhook_data_path = join(
                            data_path, join('webhook', 'default_event')
                        )
                        default_conf = {
                            'github_token': 'GHT',
                            'gitlab_token': 'GLT',
                            'vhost_path': 'VHP'
                        }
                        proc = Mock()
                        proc.wait.return_value = True
                        proc.ready.return_value = True
                        proc.get.return_value = (-1, 'fail_hook')

                        pool = Mock()
                        pool.apply_async.return_value = proc

                        pooler.start()
                        pooler.return_value = pool

                        logging.start()
                        logging.basicConfig.return_value = True
                        logging.info = True
                        logger = Mock()
                        logger.info.return_value = True
                        logger.error.return_value = True
                        logging.getLogger.return_value = logger

                        hook_used = Mock()
                        hook_used.get_args.return_value = {}
                        hook_used.run_hook = lambda *a: True

                        get_hook_mock.start()
                        get_hook_list = [('hook_name', hook_used)]
                        get_hook_mock.return_value = get_hook_list

                        parser = HookParser(webhook_data_path,
                                            event='default_event',
                                            procs=1)
                        res = parser.run_event_hooks(def_conf=default_conf)
                        expected_code = -1
                        expected_log = '[hook_name]:Failed!\n'
                        expect(res).to(equal((expected_code, expected_log)))

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
