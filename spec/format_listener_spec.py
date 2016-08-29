from os.path import abspath, normpath, dirname, join
from json import loads
from listener import hook_listener
from expects import *

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)              # Project Directory
data_path = join(project_path, 'test_data')  # Test Directory

with description('Hook Listener'):
    with it('must return a hook with "webhook" origin if used webhook'
            ' test_data on instancer method'):
        webhook_data_path = join(data_path, join('webhook', 'default_event'))
        webhook_data = loads(open(webhook_data_path, 'r').read())
        hook = hook_listener.instancer(webhook_data)
        expect(hook.origin).to(equal('webhook'))

    with it('must return a hook with "gitlab" origin if used gitlab'
            ' test_data on instancer method'):
        webhook_data_path = join(data_path, join('gitlab', 'issue.json'))
        webhook_data = loads(open(webhook_data_path, 'r').read())
        hook = hook_listener.instancer(webhook_data)
        expect(hook.origin).to(equal('gitlab'))

    with it('must return a hook with "github" origin if used github'
            ' test_data on instancer method'):
        webhook_data_path = join(data_path, join('github', 'status.json'))
        webhook_data = loads(open(webhook_data_path, 'r').read())
        hook = hook_listener.instancer(webhook_data)
        expect(hook.origin).to(equal('github'))
