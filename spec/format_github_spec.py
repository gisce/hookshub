from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from json import loads
from hooks.github import GitHubWebhook as github
from expects import *

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir

hook_testing = 'github'
data_path = join(project_path, join('test_data', hook_testing))

with description('Github Hook'):
    with context('Basic info'):
        with it('must have github as origin'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.origin).to(equal(hook_testing))

        with it('must have project_path/hooks/github as actions_path'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.actions_path).to(equal(join(
                project_path, join('hooks', hook_testing)
            )))

        with it('must contain all actions in actions directory'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            actions = listdir(hook.actions_path)
            actions = [
                action for action in actions
                if isfile(join(hook.actions_path, action))
                ]
            expect(hook.actions).to(equal(actions))

        with it('must have all actions of the situation (more details'
                ' in the readme, event-actions)'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
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

        with it('must return the same params with the get_exe_action and'
                ' with the get_test_action'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
            hook.get_exe_action(event)
            ))
            
    with context('Member event'):
        with it('must have member as event'):
            event = 'member'
            file = 'member.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('member'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the member event'):
            event = 'member'
            file = 'member.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps

            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'member'
            file = 'member.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))
            
    with context('Membership event'):
        with it('must have membership as event'):
            event = 'membership'
            file = 'membership.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('membership'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the membership event'):
            event = 'membership'
            file = 'membership.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps

            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'membership'
            file = 'membership.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))
            
    with context('Page Build event'):
        with it('must have page_build as event'):
            event = 'page_build'
            file = 'page_build.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('page_build'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the page_build event'):
            event = 'page_build'
            file = 'page_build.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps

            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'page_build'
            file = 'page_build.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))
            
    with context('Public event'):
        with it('must have public as event'):
            event = 'public'
            file = 'public.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('public'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the public event'):
            event = 'public'
            file = 'public.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps

            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'public'
            file = 'public.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

    with context('Pull Request event'):
        with it('must have pull_request as event'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('pull_request'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the pull_request'
                ' event'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

        with it('must return branch name from payload parse '
                '("master" on pull_request.json)'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name()).to(equal('master'))

    with context('Review Comment on Pull Request event'):
        with it('must have pull_request_review_comment as event'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('pull_request_review_comment'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the pull_request_review_comment'
                ' event'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

        with it('must return branch name from payload parse '
                '("master" on pull_request_review_comment.json)'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name()).to(equal('master'))

    with context('Push event'):
        with it('must have push as event'):
            event = 'push'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('push'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the push event'):
            event = 'push'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'push'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

        with it('must return branch name from payload parse '
                '("changes" on push.json)'):
            event = 'push'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name()).to(equal('changes'))

    with context('Release event'):
        with it('must have release as event'):
            event = 'release'
            file = 'release.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('release'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the release event'):
            event = 'release'
            file = 'release.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'release'
            file = 'release.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

    with context('Repository event'):
        with it('must have repository as event'):
            event = 'repository'
            file = 'repository.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('repository'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the repository event'):
            event = 'repository'
            file = 'repository.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'repository'
            file = 'repository.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

    with context('Status event'):
        with it('must have status as event'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('status'))

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

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

        with it('must return status from payload (success on status.json)'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.status()).to(equal('success'))

    with context('Team Add event'):
        with it('must have team_add as event'):
            event = 'team_add'
            file = 'team_add.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('team_add'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the team_add event'):
            event = 'team_add'
            file = 'team_add.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'team_add'
            file = 'team_add.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))

    with context('Watch event'):
        with it('must have watch as event'):
            event = 'watch'
            file = 'watch.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('watch'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the watch event'):
            event = 'watch'
            file = 'watch.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            from json import dumps
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event)).to(equal(exe_data))

        with it('must return the execution params to test the action, if there'
                ' isn\'t any, it may return the same as the execution params'):
            event = 'watch'
            file = 'watch.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.get_test_action(event)).to(equal(
                hook.get_exe_action(event)
            ))
