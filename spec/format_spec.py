from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from json import loads
from hooks.webhook import webhook
from expects import *

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir


with description('Generic hook (webhook)'):
    with context('Using default_event json'):
        with it('Hook Origin must be webhook'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            expect(hook.origin).to(equal('webhook'))

        with it('Hook Event must be default_event'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            expect(hook.event).to(equal('default_event'))

        with it('Hook action path must be project_path/hooks/webhook'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            expect(hook.actions_path).to(equal(join(
                project_path, join('hooks', hook_testing)
            )))

        with it('Actions must only contain default_event'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            expect(len(hook.actions)).to(equal(1))
            expect(hook.actions[0]).to(equal('default_event'))

        with it('Actions may return the same as event_actions'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            expect(hook.actions).to(equal(hook.event_actions))

        with it('Getting exe for action must return'
                ' [exe_path, dump(json), event]'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            exe_path = join(hook.actions_path, 'default_event')
            event = 'default_event'
            from json import dumps
            data = dumps(loads(data))
            expect(len(hook.get_exe_action(event))).to(equal(3))
            expect(hook.get_exe_action(event)[0]).to(equal(exe_path))
            expect(hook.get_exe_action(event)[1]).to(equal(data))
            expect(hook.get_exe_action(event)[2]).to(equal(event))

        with it('Getting exe for test must return the same as exec'):
            hook_testing = 'webhook'
            file = 'default_event'
            data_path = join(project_path, join('test_data', hook_testing))
            data = open(join(data_path, file), 'r').read()
            hook = webhook(loads(data))
            expect(hook.get_test_action('default_event')).to(equal(
                hook.get_exe_action('default_event')
            ))
