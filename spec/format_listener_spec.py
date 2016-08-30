from os.path import abspath, normpath, dirname, join
from json import loads
from listener import HookListener
from expects import *

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
