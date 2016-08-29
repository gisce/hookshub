from os.path import abspath, normpath, dirname, join
from json import loads
from hooks.webhook import webhook
from expects import *

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir

hook_testing = 'webhook'
event = 'default_event'
file = 'default_event'
data_path = join(project_path, join('test_data', hook_testing))
data = open(join(data_path, file), 'r').read()

with description('Generic hook (webhook) - Default Event'):
    with it('must have webhook as origin'):
        hook = webhook(loads(data))
        expect(hook.origin).to(equal('webhook'))

    with it('must have default_event as event'):
        hook = webhook(loads(data))
        expect(hook.event).to(equal(event))

    with it('must have project_path/hooks/webhook as actions_path'):
        hook = webhook(loads(data))
        expect(hook.actions_path).to(equal(join(
            project_path, join('hooks', hook_testing)
        )))

    with it('must only contain default_event within actions'):
        hook = webhook(loads(data))
        expect(len(hook.actions)).to(equal(1))
        expect(hook.actions[0]).to(equal(event))

    with it('must have the same list on both, actions and event_actions'):
        hook = webhook(loads(data))
        expect(hook.actions).to(equal(hook.event_actions))

    with it('must return [exe_path, dump(json), event] when getting'
            ' the execution params for the default event'):
        hook = webhook(loads(data))
        exe_path = join(hook.actions_path, event)
        from json import dumps
        json_data = dumps(loads(data))
        expect(len(hook.get_exe_action(event))).to(equal(3))
        expect(hook.get_exe_action(event)[0]).to(equal(exe_path))
        expect(hook.get_exe_action(event)[1]).to(equal(json_data))
        expect(hook.get_exe_action(event)[2]).to(equal(event))

    with it('must return the same params with the get_exe_action and'
            ' with the get_test_action'):
        hook = webhook(loads(data))
        expect(hook.get_test_action(event)).to(equal(
            hook.get_exe_action(event)
        ))
