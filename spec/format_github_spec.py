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

hook_path = 'github_hooks'
hook_testing = 'github'
data_path = join(project_path, join('test_data', hook_testing))

with description('GitHub Hook'):
    with context('Basic info'):
        with it('must have github as origin'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.origin).to(equal(hook_testing))

        with it('must have project_path/hooks/github_hooks as actions_path'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.actions_path).to(equal(join(
                project_path, 'hookshub', 'hooks', hook_path
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

        with it('may return "None" when trying to get target branch name for a '
                'non-target-branch event'):
            file = 'status.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.target_branch_name).to(equal('None'))

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

        with it('Must return "None" when getting "action" and event!='
                ' "pull_request"'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.action).to(equal("None"))

        with it('Must return "None" when getting "number" and event'
                ' does not have #number (pr, pr_comm, issue, issue_comm)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.number).to(equal("None"))

        with it('Must return "False" when getting "merged" property and event'
                'is not "pull_request" or it\'s merged'):
            event = 'push'
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.merged).to(equal(False))

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

        with it('Must return the #number when getting "number" ("1")'):
            file = 'issue_comment.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.number).to(equal(2))
            
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

        with it('Must return the #number when getting "number" ("1")'):
            file = 'issues.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.number).to(equal(2))
            
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
                '("changes" on pull_request.json)'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('changes'))

        with it('must return target branch name from payload parse'
                '("master" on pull_request.json)'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.target_branch_name).to(equal('master'))

        with it('must return if the pull_request is merged or not'):
            event = 'pull_request'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.merged).to(equal(True))
            json_data['pull_request']['merged'] = False
            hook = github(json_data)
            expect(hook.merged).to(equal(False))

        with it('Must return action status when getting "action" ("opened")'):
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.action).to(equal("opened"))

        with it('Must have action status "closed", Merged status "false"'
                ' and return "closed" "true"'):
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            json_data['action'] = 'closed'
            json_data['pull_request']['merged'] = False
            hook = github(json_data)
            expect(hook.closed).to(equal(True))

        with it('Must have action status "closed", Merged status "true"'
                ' and return "closed" "false"'):
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            json_data['action'] = 'closed'
            hook = github(json_data)
            expect(hook.closed).to(equal(False))

        with it('Must return the #number when getting "number" ("1")'):
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.number).to(equal(1))

    with context('Pull Request Review event'):
        with it('must have pull_request_review as event'):
            event = 'pull_request_review'
            file = 'pull_request_review.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(
                hook.event
            ).to(equal(
                util.events['EVENT_PULL_REQUEST_REVIEW']
            ))

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
                '("changes" on pull_request_review_comment.json)'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.branch_name).to(equal('changes'))

        with it('must return target branch name from payload parse '
                '("master" on pull_request_review_comment.json)'):
            event = 'pull_request_review_comment'
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            expect(hook.target_branch_name).to(equal('master'))

        with it('Must return the #number when getting "number" ("1")'):
            file = 'pull_request_review_comment.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = github(json_data)
            expect(hook.number).to(equal(1))

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
                ' repo_name, the pr_number and the action'):
            event = 'pull_request-powerp-docs'
            file = 'pull_request.json'
            data = open(join(data_path, file)).read()
            hook = github(loads(data))
            exe_path = join(hook.actions_path, event)

            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            json = {}
            json.update({'token': config['github_token']})
            json.update({'vhost_path': config['vhost_path']})
            json.update({'port': config['nginx_port']})
            json.update({'ssh_url': hook.ssh_url})
            json.update({'http_url': hook.http_url})
            json.update({'repo_name': hook.repo_name})
            json.update({'repo_full_name': hook.repo_full_name})
            json.update({'branch_name': hook.branch_name})
            json.update({'action': hook.action})
            json.update({'number': hook.number})
            json.update({'merged': hook.merged})
            json.update({'closed': hook.closed})

            json_data = dumps(json)
            args_json = loads(hook.get_exe_action(event, config)[1])
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
        with it('Must try to pip install on a dir and log it correctly'):
            with patch("hookshub.hooks.github.os") as os:
                os.start()
                os.system = lambda x: 0
                log = util.pip_requirements(data_path)
                with open(join(
                        project_path, 'test_data', 'utils', 'pip_install_ok'
                ), 'r') as out:
                    output = out.read()
                expect(log).to(equal(output))

        with it('Must try to pip install on a dir. Failing must log correctly'):
            with patch("hookshub.hooks.github.os") as os:
                os.start()
                os.system = lambda x: -1
                log = util.pip_requirements(data_path)
                with open(join(
                        project_path, 'test_data', 'utils', 'pip_install_bad'
                ), 'r') as out:
                    output = out.read()
                expect(log).to(equal(output))

    # export PYTHONPATH
    with context('Export PYTHONPATH with sitecustomize'):
        with it('Must return a log with a success message when seting the var'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['All Ok\n']
                popen_mock.returncode = 0
                popen.return_value = popen_mock
                log = util.export_pythonpath('Path')
                expect(len(log) > 0).to(equal(True))
                expect(log).to(equal('Success to export sitecustomize path'))
                popen.stop()

        with it('Must return a log with a failure message when seting the var'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['All Bad\n']
                popen_mock.returncode = -1
                popen.return_value = popen_mock
                log = util.export_pythonpath('Path')
                expect(len(log) > 0).to(equal(True))
                expect(log).to(equal('Failed to export sitecustomize path'))
                popen.stop()

        with it('Must return a log with a failure message when seting the var'
                'and an exception is thrown'):
            with patch("hookshub.hooks.github.Popen") as popen:
                popen.start()
                popen.side_effect = Exception('Mocked exception')
                popen.return_value = 0
                log = util.export_pythonpath('Path')
                expect(len(log) > 0).to(equal(True))
                expect(log).to(equal(
                    'Failed to export sitecustomize path'
                ))
                popen.stop()

    # docs_build
    with context('Build docs'):
        with it('Must return $log + $build_dir with correct docs build'):
            with patch("hookshub.hooks.github.os") as os:
                os.start()
                os.system = lambda x: 0
                from_path = 'From docs'
                to_path = 'To build'
                file = 'Config File'
                log, dir = util.docs_build(from_path, to_path, file, True)
                with open(join(
                        project_path, 'test_data', 'utils', 'build_ok'
                ), 'r') as out:
                    output = out.read()
                expect(log).to(equal(output))
                expect(dir).to(equal(to_path))
                os.stop()

        with it('Must return $log + "False" with bad docs build'):
            with patch("hookshub.hooks.github.os") as os:
                os.start()
                os.system = lambda x: -1
                from_path = 'From docs'
                to_path = 'To build'
                file = 'Config File'
                log, dir = util.docs_build(from_path, to_path, file)
                with open(join(
                        project_path, 'test_data', 'utils', 'build_bad'
                ), 'r') as out:
                    output = out.read()
                expect(log).to(equal(output))
                expect(dir).to(equal(False))
                os.stop()

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

        with it('Must return a error code if status code != 201 (Mocked)'):
            with patch("hookshub.hooks.github.requests.post") as req_get:
                req_get.start()


                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)


                req_get.return_value = MockedReturn(400, [])
                code, log = util.post_comment_pr(
                    'Token', 'Repository', 1234, 'Comment'
                )
                expect(code).to(equal(400))
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

    # GitHub data
    with context('Events and globals'):
        with it('Must have the events property with a dictionary of the '
                'GitHub events that the hook is able to read and process'):
            events = {
                'EVENT_COMMIT_COMMENT': 'commit_comment',
                'EVENT_CREATE': 'create',
                'EVENT_DELETE': 'delete',
                'EVENT_DEPLOYMENT': 'deployment',
                'EVENT_DEPLOYMENT_STATUS': 'deployment_status',
                'EVENT_FORK': 'fork',
                'EVENT_WIKI': 'gollum',
                'EVENT_ISSUE_COMMENT': 'issue_comment',
                'EVENT_ISSUE': 'issues',
                'EVENT_MEMBER': 'member',
                'EVENT_MEMBERSHIP': 'membership',
                'EVENT_PAGE_BUILD': 'page_build',
                'EVENT_PUBLIC_EVENT': 'public',
                'EVENT_PULL_REQUEST': 'pull_request',
                'EVENT_PULL_REQUEST_REVIEW': 'pull_request_review_comment',
                'EVENT_REVIEW_PR_COMMENT': 'pull_request_review_comment',
                'EVENT_PUSH': 'push',
                'EVENT_RELEASE': 'release',
                'EVENT_REPOSITORY': 'repository',
                'EVENT_STATUS': 'status',
                'EVENT_TEAM_ADD': 'team_add',
                'EVENT_WATCH': 'watch'
            }
            for key in events.keys():
                name = util.events.get(key, False)
                expect(name).to(equal(events[key]))
            for key in util.events.keys():
                name = events.get(key, False)
                expect(name).to(equal(util.events[key]))

        with it('Must have the actions property with a dictionary of the'
                'GitHub Pull Request actions property that the hook is able'
                'to read from the hook'):
            actions = {
                'ACT_ASSIGNED': 'assigned',
                'ACT_UNASSIGN': 'unassigned',
                'ACT_LABELED': 'labeled',
                'ACT_UNLABELED': 'unlabeled',
                'ACT_OPENED': 'opened',
                'ACT_EDITED': 'edited',
                'ACT_CLOSED': 'closed',
                'ACT_REOPENED': 'reopened',
                'ACT_SYNC': 'synchronize',
                'ACT_CREATED': 'created'
            }
            for key in actions.keys():
                name = util.actions.get(key, False)
                expect(name).to(equal(actions[key]))
            for key in util.actions.keys():
                name = actions.get(key, False)
                expect(name).to(equal(util.actions[key]))
