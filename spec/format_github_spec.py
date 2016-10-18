from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from json import loads, dumps

from hookshub.hooks.github import GitHubWebhook as github
from hookshub.hooks.github import GitHubUtil as util

from expects import *
from mock import patch, Mock

import requests

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir

hook_testing = 'github'
data_path = join(project_path, join('test_data', hook_testing))

with description('GitHub Hook'):
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
                project_path, join(
                    'hookshub', join('hooks', hook_testing)
                )
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
            expect(hook.ssh_url).to(equal(
                json_data['repository']['ssh_url']
            ))

        with it('must return the html url of the repository'
                ' (json/repository/clone_url)'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.http_url).to(equal(
                json_data['repository']['clone_url']
            ))

        with it('must return the name of the repository'
                ' (json/repository/name)'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.repo_name).to(equal(
                json_data['repository']['name']
            ))

        with it('may return "None" when trying to get branch name for a '
                'non-branch event'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.branch_name).to(equal('None'))

        with it('may return "None" when trying to get status for an event '
                'that isn\'t state'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.status).to(equal('None'))

        with it('must return the repository ID from the repository of the hook'
                '(35129377 on push.json)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.repo_id).to(equal(35129377))

    with context('Commit Comment event'):
        with it('must have commit_comment as event'):
            event = 'commit_comment'
            file = 'commit_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('commit_comment'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the commit_comment event'):
            event = 'commit_comment'
            file = 'commit_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
    with context('Create event'):
        with it('must have create as event'):
            event = 'create'
            file = 'create.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('create'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the create event'):
            event = 'create'
            file = 'create.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

        with it('must return None from payload if ref != branch '
                '(ref == tag on create.json)'):
            event = 'create'
            file = 'create.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('None'))
            
    with context('Delete event'):
        with it('must have delete as event'):
            event = 'delete'
            file = 'delete.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('delete'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the delete event'):
            event = 'delete'
            file = 'delete.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

        with it('must return branch name from payload if ref == branch '
                '(branch_to_delete from delete.json)'):
            event = 'delete'
            file = 'delete.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('branch_to_delete'))
            
    with context('Deployment event'):
        with it('must have deployment as event'):
            event = 'deployment'
            file = 'deployment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('deployment'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the deployment event'):
            event = 'deployment'
            file = 'deployment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
    with context('Deployment Status event'):
        with it('must have deployment_status as event'):
            event = 'deployment_status'
            file = 'deployment_status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('deployment_status'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the deployment_status event'):
            event = 'deployment_status'
            file = 'deployment_status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
    with context('Fork event'):
        with it('must have fork as event'):
            event = 'fork'
            file = 'fork.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('fork'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the fork event'):
            event = 'fork'
            file = 'fork.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
    with context('Documentation (Gollum) event'):
        with it('must have gollum as event'):
            event = 'gollum'
            file = 'gollum.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('gollum'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the gollum event'):
            event = 'gollum'
            file = 'gollum.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
    with context('Issue Comment event'):
        with it('must have issue_comment as event'):
            event = 'issue_comment'
            file = 'issue_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('issue_comment'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the issue_comment event'):
            event = 'issue_comment'
            file = 'issue_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
    with context('Issues event'):
        with it('must have issues as event'):
            event = 'issues'
            file = 'issues.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.event).to(equal('issues'))

        with it('must return [exe_path, dump(json), event] when getting'
                ' the execution params for the issues event'):
            event = 'issues'
            file = 'issues.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
            
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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

        with it('must return branch name from payload parse '
                '("master" on pull_request.json)'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('master'))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

        with it('must return branch name from payload parse '
                '("master" on pull_request_review_comment.json)'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('master'))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

        with it('must return branch name from payload parse '
                '("changes" on push.json)'):
            event = 'push'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('changes'))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))
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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

        with it('must return status from payload (success on status.json)'):
            event = 'status'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.status).to(equal('success'))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

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
            
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            dict_json = loads(data)
            json_data = dumps(dict_json)
            exe_data = [exe_path, json_data, event]
            expect(hook.get_exe_action(event, config)).to(equal(exe_data))

    with context('Bad JSON for push event'):
        with it('must return push as event'):
            file = 'bad_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.event).to(equal('push'))

        with it('must return None as branch name'):
            file = 'bad_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.branch_name).to(equal('None'))

    with context('With powerp-docs repository events'):
        with it('must return token, port, ssh and http url, repository and'
                ' branch names and state; with "status-powerp-docs.py" action'
                ' arguments from hook'):
            action = 'status-powerp-docs.py'
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            # Set required data from default data:
            json_data['repository']['name'] = 'powerp-docs'
            hook = github(json_data)
            json = {}
            json.update({'ssh_url': hook.ssh_url})
            json.update({'http_url': hook.http_url})
            json.update({'repo-name': hook.repo_name})
            json.update({'branch-name': hook.branch_name})
            json.update({'state': hook.status})
            args_json = loads(hook.get_exe_action(action, config)[1])
            checked = []
            for key in args_json.keys():
                checked.append(key)
                expect(args_json[key]).to(
                    equal(json.get(key, '{} Not found'.format(key)))
                )
            for key in json.keys():
                expect(checked).to(contain(key))

        with it('must return token, port, vhost path, ssh and http urls, '
                'repository and branch names, full repository name;'
                ' with "push-powerp-docs.py" action arguments from hook'):
            action = 'push-powerp-docs.py'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            # Set required data from default data:
            json_data['repository']['name'] = 'powerp-docs'
            hook = github(json_data)
            json = {}
            json.update({'token': config['github_token']})
            json.update({'port': config['nginx_port']})
            json.update({'vhost_path': config['vhost_path']})
            json.update({'ssh_url': hook.ssh_url})
            json.update({'http_url': hook.http_url})
            json.update({'repo_name': hook.repo_name})
            json.update({'repo_full_name': hook.repo_full_name})
            json.update({'branch_name': hook.branch_name})
            args_json = loads(hook.get_exe_action(action, config)[1])
            checked = []
            for key in args_json.keys():
                checked.append(key)
                expect(args_json[key]).to(
                    equal(json.get(key, '{} Not found'.format(key)))
                )
            for key in json.keys():
                expect(checked).to(contain(key))

        with it('must return [exe_path, payload, event] when getting'
                ' the execution params for the pull_request event.'
                ' Payload must include: vhost_path, ssh and http url,'
                ' repo_name and if it\'s merged'):
            action = 'pull_request-powerp-docs'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, action)

            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            json = {}
            json.update({'vhost_path': config['vhost_path']})
            json.update({'ssh_url': hook.ssh_url})
            json.update({'http_url': hook.http_url})
            json.update({'repo_name': hook.repo_name})
            json.update({'merged': hook.merged})
            args_json = loads(hook.get_exe_action(action, config)[1])
            checked = []
            for key in args_json.keys():
                checked.append(key)
                expect(args_json[key]).to(
                    equal(json.get(key, '{} Not found'.format(key)))
                )
            for key in json.keys():
                expect(checked).to(contain(key))

with description('GitHub Utils'):
    # clone_on_dir
    with context('Clone on Dir'):
        with it('Must return a String and a returncode == 0 with the '
                'right params(mocked)'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['All Ok\n', '']
                popen_mock.returncode = 0
                popen.return_value = popen_mock
                log, result, err = util.clone_on_dir(
                    'directory', 'branch', 'repository', 'github url'
                )
                expect(len(log) > 0).to(equal(True))
                expect(len(err)).to(equal(0))
                expect(result).to(equal(0))
                popen.stop()

        with it('Must return a String and a returncode != 0 with the '
                'wrong params(mocked)'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['Not Ok\n', 'Mocked!']
                popen_mock.returncode = 1
                popen.return_value = popen_mock
                log, result, err = util.clone_on_dir(
                    'directory', 'branch', 'repository', 'github url'
                )
                expect(len(log) > 0).to(equal(True))
                expect(len(err) > 0).to(equal(True))
                expect(result).to(equal(1))
                popen.stop()

    # pip_requirements
    with context('Install pip requirements'):
        with it('Must try to pip install on a dir. If can\'t it\'ll print'
                ' another line with the error'):
            log = util.pip_requirements(data_path)
            expect(len(log) > 0).to(equal(True))

    # docs_build
    with context('Build docs'):
        with it('Must return two strings (log + build dir -> Mocked)'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['All Ok\n', 'Mocked!']
                popen_mock.returncode = 0
                popen.return_value = popen_mock
                from_path = 'From docs'
                to_path = 'To build'
                log, dir = util.docs_build(from_path, to_path)
                expect(len(log) > 0).to(equal(True))
                expect(dir).to(equal(to_path))
                popen.stop()

        with it('Must return the log String and a False directory (Mocked)'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['All Ok\n', 'Mocked!']
                popen_mock.returncode = 1
                popen.return_value = popen_mock
                from_path = 'From docs'
                to_path = 'To build'
                log, dir = util.docs_build(from_path, to_path)
                expect(len(log) > 0).to(equal(True))
                expect(dir).to(equal(False))
                popen.stop()

    # get_pr
    with context('Get Pull Request'):
        with it('Must return code with get request (Mocked)'):
            with patch("hookshub.hooks.github.requests") as req_get:
                req_get.start()

                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)

                req_get.get.return_value = MockedReturn(
                    200, [
                            {
                                'id': 1,
                                'head': {
                                    'ref': 'Branch'
                                }
                            }
                        ]
                )
                code, log = util.get_pr(
                    'Token', 'Repository', 'Branch'
                )
                expect(code['id']).to(equal(1))
                req_get.stop()

        with it('Must rise an internal error if did not get a 200 status'
                ' response (Mocked)'):
            with patch("hookshub.hooks.github.requests") as req_get:
                req_get.start()

                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)

                req_get.get.return_value = MockedReturn(
                    300, []
                )
                code, log = util.get_pr(
                    'Token', 'Repository', 'Branch'
                )
                expect(code).to(equal(-1))
                req_get.stop()

        with it('Must rise an internal error if did not get any matching prs'
                ' response (Mocked)'):
            with patch("hookshub.hooks.github.requests") as req_get:
                req_get.start()


                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)


                req_get.get.return_value = MockedReturn(
                    200, []
                )
                code, log = util.get_pr(
                    'Token', 'Repository', 'Branch'
                )
                expect(code).to(equal(-1))
                req_get.stop()

        with it('Must rise an internal error if an http exception is thrown'
                ' (Mocked)'):
            with patch("hookshub.hooks.github.requests.get") as req_get:
                req_get.start()
                req_get.side_effect = requests.HTTPError('Mocked Error')
                code, log = util.get_pr(
                    'Token', 'Repository', 'Branch'
                )
                expect(code).to(equal(-1))
                req_get.stop()

        with it('Must rise an internal error if a connection exception is'
                ' thrown (Mocked)'):
            with patch("hookshub.hooks.github.requests.get") as req_get:
                req_get.start()
                req_get.side_effect = requests.ConnectionError('Mocked Error')
                code, log = util.get_pr(
                    'Token', 'Repository', 'Branch'
                )
                expect(code).to(equal(-1))
                req_get.stop()

        with it('Must rise an internal error if a request exception is'
                ' thrown (Mocked)'):
            with patch("hookshub.hooks.github.requests.get") as req_get:
                req_get.start()
                req_get.side_effect = requests.RequestException('Mocked Error')
                code, log = util.get_pr(
                    'Token', 'Repository', 'Branch'
                )
                expect(code).to(equal(-1))
                req_get.stop()

        with it('Must return -1 when bad params on call'):
            code, log = util.get_pr(
                'Token', False, False
            )
            expect(code).to(equal(-1))

    # post_comment_pr
    with context('Post Comment On PR'):
        with it('Must return a 201 status code if all OK (Mocked)'):
            with patch("hookshub.hooks.github.requests.post") as req_get:
                req_get.start()

                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)

                req_get.return_value = MockedReturn(201, [])
                code, log = util.post_comment_pr(
                    'Token', 'Repository', 1234, 'Comment'
                )
                expect(code).to(equal(201))
                req_get.stop()

        with it('Must raise an internal error if a connection exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.github.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = requests.ConnectionError('Mocked Error')
                code, log = util.post_comment_pr(
                    'Token', 'Repository', 1234, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()

        with it('Must raise an internal error if a http exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.github.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = requests.HTTPError('Mocked Error')
                code, log = util.post_comment_pr(
                    'Token', 'Repository', 1234, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()

        with it('Must raise an internal error if a request exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.github.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = requests.RequestException('Mocked Error')
                code, log = util.post_comment_pr(
                    'Token', 'Repository', 1234, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()

        with it('Must raise an internal error if an internal exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.github.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = Exception('Mocked Error')
                code, log = util.post_comment_pr(
                    'Token', 'Repository', 1234, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()
