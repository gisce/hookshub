from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from json import loads
from hooks.gitlab import GitLabWebhook as gitlab
from expects import *

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir

hook_testing = 'gitlab'
data_path = join(project_path, join('test_data', hook_testing))

with description('Gitlab Hook'):
    with context('Basic info'):
        with it('must have gitlab as origin'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = gitlab(loads(data))
            expect(hook.origin).to(equal(hook_testing))

        with it('must have project_path/hooks/gitlab as actions_path'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = gitlab(loads(data))
            expect(hook.actions_path).to(equal(join(
                project_path, join('hooks', hook_testing)
            )))

        with it('must contain all actions in actions directory'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = gitlab(loads(data))
            actions = listdir(hook.actions_path)
            actions = [
                action for action in actions
                if isfile(join(hook.actions_path, action))
                ]
            expect(hook.actions).to(equal(actions))

        with it('must have all actions of the situation (more details'
                ' in the readme, event-actions)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = gitlab(loads(data))
            actions = listdir(hook.actions_path)
            actions = [
                action for action in actions
                if isfile(join(hook.actions_path, action))
                ]
            actions = [
                action
                for action in actions
                # If they start with {event}-{repository}-{branch}
                if action.startswith('{0}-{1}-{2}'.format(
                    hook.event, hook.repo_name, hook.branch_name
                )) or
                # If they start with {event}-{repository}_{name}
                action.startswith(
                    '{0}-{1}_'.format(hook.event, hook.repo_name)) or
                # If they are named after {event}-{repository}
                action == '{0}-{1}'.format(hook.event, hook.repo_name) or
                # If they start with {event}_{name}
                action.startswith('{0}_'.format(hook.event)) or
                # If they are named after {event}
                action == '{0}'.format(hook.event)
                ]
            expect(hook.event_actions).to(equal(actions))

        with it('must return the ssh url of the repository'
                    ' (json/repository/git_ssh_url)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.ssh_url()).to(equal(
                json_data['repository']['git_ssh_url']
            ))

        with it('must return the html url of the repository'
                ' (json/repository/git_http_url)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.http_url()).to(equal(
                json_data['repository']['git_http_url']
            ))

        with it('must return the name of the repository'
                ' (json/repository/name)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.repo_name()).to(equal(
                json_data['repository']['name']
            ))

        with it('may return the name of the branch or "None"'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            branch_name = json_data['ref'].split('/', 2)[-1]
            hook = gitlab(json_data)
            expect(hook.branch_name()).to(equal(branch_name))