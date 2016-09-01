from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from json import loads, dumps
from hookshub.hooks.gitlab import GitLabWebhook as gitlab
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
                project_path, join(
                    'hookshub', join('hooks', hook_testing)
                )
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
            expect(hook.ssh_url).to(equal(
                json_data['repository']['git_ssh_url']
            ))

        with it('must return the html url of the repository'
                ' (json/repository/git_http_url)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.http_url).to(equal(
                json_data['repository']['git_http_url']
            ))

        with it('must return the name of the repository'
                ' (json/repository/name)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.repo_name).to(equal(
                json_data['repository']['name']
            ))

        with it('may return "None" when getting branch name '
                'on non-branch event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.branch_name).to(equal('None'))

        with it('may return [action path, dumps(payload), event] as default'
                ' action args getter'):
            file = 'tag_push.json'
            action = 'tag_push_non_existing_action'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            action_path = join(hook.actions_path, action)
            args = [action_path, dumps(json_data), 'tag_push']
            expect(hook.get_exe_action(action)).to(equal(args))

        with it('must return "None" when getting target branch on a non-target'
                '-branch event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.target_branch_name).to(equal('None'))

    with context('Comment Event'):
        with it('must have "note" as event'):
            file = 'comment_code.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.event).to(equal('note'))

        with it('may return none when getting branch name if commenting'
                ' something else (not request or issue)'):
            file = 'comment_commit.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.branch_name).to(equal('None'))

        with context('Commenting an Issue'):
            with it('may return branch name if commenting issue related to a branch'
                    ' or None if not related (None on comment_issue.json)'):
                file = 'comment_issue.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                expect(hook.branch_name).to(equal('None'))

        with context('Commenting a Merge Request'):
            with it('may return source branch name if commenting request '
                    '(markdown on comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                expect(hook.branch_name).to(equal('markdown'))

            with it('may return target branch name if commenting request '
                    '(master on comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                expect(hook.target_branch_name).to(equal('master'))

            with it('must return ssh url from merge_request source'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                url = json_data['merge_request']['source']['git_ssh_url']
                expect(hook.ssh_url).to(equal(url))

            with it('must return http url from merge_request source'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                url = json_data['merge_request']['source']['git_http_url']
                expect(hook.http_url).to(equal(url))

            with it('must return repository name from merge_request source'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                name = json_data['merge_request']['source']['name']
                expect(hook.repo_name).to(equal(name))

    with context('Issue Event'):
        with it('must have "issue" as event'):
            file = 'issue.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.event).to(equal('issue'))

        with it('may return branch name if the issue is related to a branch'
                ' or None if not related (None on issue.json)'):
            file = 'issue.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.branch_name).to(equal('None'))

    with context('Merge Request Event'):
        with it('must have "merge_request" as event'):
            file = 'merge_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.event).to(equal('merge_request'))

        with it('must return source branch name (ms-viewport on '
                'merge_request.json)'):
            file = 'merge_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.branch_name).to(equal('ms-viewport'))

        with it('must return target branch name (master on'
                'merge_request.json)'):
            file = 'merge_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.target_branch_name).to(equal('master'))

    with context('Push Event'):
        with it('must have "push" as event'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.event).to(equal('push'))

        with it('may return branch name (master on push.json)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.branch_name).to(equal('master'))

    with context('Tag Push Event'):
        with it('must have "tag_push" as event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.event).to(equal('tag_push'))

    with context('Bad JSON for push event'):
        with it('must return push as event'):
            file = 'bad_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.event).to(equal('push'))

        with it('must return None as branch name'):
            file = 'bad_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.branch_name).to(equal('None'))

    with context('Lektor repository events'):
        with it('must return specific json on Merge_Request Event (must'
                ' contain: ssh and http url, repository name and source'
                ' branch name)'):
            file = 'merge_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            json = {}
            json.update({'ssh_url': hook.ssh_url})
            json.update({'http_url': hook.http_url})
            json.update({'repo_name': hook.repo_name})
            json.update({'branch_name': hook.branch_name})
            expect(hook.get_exe_action('merge_request_lektor.py')[1]).to(
                equal(dumps(json))
            )
