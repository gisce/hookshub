from os.path import abspath, normpath, dirname, join
from json import loads
from hooks.github import GitHubWebhook as github
from expects import *

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir

hook_testing = 'github'
data_path = join(project_path, join('test_data', hook_testing))

with description('Github Hook'):
    with context('Status event'):
        with it('must have github as origin'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.origin).to(equal(hook_testing))

        with it('must have status as event'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('status'))

        with it('must have project_path/hooks/github as actions_path'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.actions_path).to(equal(join(
                project_path, join('hooks', hook_testing)
            )))

        with it('must only contain status-powerp-docs within actions'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(len(hook.actions)).to(equal(1))
            expect(hook.actions[0]).to(equal('status-powerp-docs'))

        with it('must have status actions only in event_actions, actually 0'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(len(hook.event_actions)).to(equal(0))

        with it('must return the ssh url of the repository'
                ' (json/repository/ssh_url)'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.ssh_url()).to(equal(
                json_data['repository']['ssh_url']
            ))

        with it('must return the html url of the repository'
                ' (json/repository/clone_url)'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.http_url()).to(equal(
                json_data['repository']['clone_url']
            ))

        with it('must return the name of the repository'
                ' (json/repository/name)'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.repo_name()).to(equal(
                json_data['repository']['name']
            ))

        with it('may return the name of the branch or "None"'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.branch_name()).to(equal('None'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the status event'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = {}
            dict_json.update({'ssh_url': hook.ssh_url()})
            dict_json.update({'http_url': hook.http_url()})
            dict_json.update({'repo-name': hook.repo_name()})
            dict_json.update({'branch-name': hook.branch_name()})
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the same params with the get_exe_action and'
                ' with the get_test_action'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))
