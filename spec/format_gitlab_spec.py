from os.path import abspath, normpath, dirname, join, isfile, isdir
from os import listdir
from json import loads, dumps
from hookshub.hooks.gitlab import GitLabWebhook as gitlab
from hookshub.hooks.gitlab import GitLabUtil as util
from expects import *
from mock import patch, Mock

import requests

my_path = normpath(abspath(dirname(__file__)))
project_path = dirname(my_path)  # project dir

hook_path = 'gitlab_hooks'
hook_testing = 'gitlab'
data_path = join(project_path, join('test_data', hook_testing))

with description('GitLab Hook'):
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
                    'hookshub', join('hooks', hook_path)
                )
            )))

        with it('must contain all actions in actions directory'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            hook = gitlab(loads(data))
            if not isdir(hook.actions_path):
                actions = []
            else:
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
            if not isdir(hook.actions_path):
                actions = []
            else:
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
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            hook = gitlab(json_data)
            json_data.update({'token': config['gitlab_token']})
            json_data.update({'port': config['nginx_port']})
            action_path = join(hook.actions_path, action)
            args = [action_path, dumps(json_data), 'tag_push']
            expect(hook.get_exe_action(action, config)).to(equal(args))

        with it('must return "None" when getting target branch on a non-target'
                '-branch event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.target_branch_name).to(equal('None'))

        with it('must return None when getting target project id on a non-'
                'target event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.target_project_id).to(equal(None))

        with it('must return None when getting item id on a non-item event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.index_id).to(equal(None))

        with it('must return None when getting object_id on a'
                ' non-merge_request event'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.object_id).to(equal(None))

        with it('must return the right project id when getting project_id'
                '(1 on tag_push.json)'):
            file = 'tag_push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.project_id).to(equal(1))

        with it('must return None when getting state property on non-state'
                'event (like push)'):
            file = 'push.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.state).to(equal('None'))

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

            with it('must return the right state of the issue that has been'
                    ' commented (/issue/state on comment_request.json)'):
                file = 'comment_issue.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                issue_state = json_data['issue']['state']
                expect(hook.state).to(equal(issue_state))

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

            with it('must return source project id if commenting request '
                    '(markdown on comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                expect(hook.project_id).to(equal(5))

            with it('must return target project id if commenting request '
                    '(master on comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                expect(hook.target_project_id).to(equal(5))

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

            with it('must return index id of the merge request that references'
                    '(/merge_request/iid on comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                merge_id = json_data['merge_request']['iid']
                expect(hook.index_id).to(equal(merge_id))

            with it('must return object id of the merge request that references'
                    '(/merge_request/id on comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                merge_id = json_data['merge_request']['id']
                expect(hook.object_id).to(equal(merge_id))

            with it('must return the right state of the merge_request that'
                    ' has been commented (/merge_request/state on'
                    ' comment_request.json)'):
                file = 'comment_request.json'
                data = open(join(data_path, file)).read()
                json_data = loads(data)
                hook = gitlab(json_data)
                merge_state = json_data['merge_request']['state']
                expect(hook.state).to(equal(merge_state))

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

        with it('must return None when getting project_id'):
            file = 'issue.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            expect(hook.project_id).to(equal(None))

        with it('must return the right state of the issue '
                '(/object_attributes/state on issue.json)'):
            file = 'issue.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            issue_state = json_data['object_attributes']['state']
            expect(hook.state).to(equal(issue_state))

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

        with it('must return target project id of the merge request '
                '(object_attributes>target_project_id on merge_request.json)'):
            file = 'merge_request.json'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            hook = gitlab(json_data)
            project_id = json_data['object_attributes']['target_project_id']
            expect(hook.target_project_id).to(equal(project_id))

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
        with it('must return token, port, vhost path, ssh and http url,'
                ' repository name and source branch name, object and index id'
                ' of the merge request when getting action arguments with '
                '"merge request" action'):
            file = 'merge_request.json'
            action = 'merge_request_lektor.py'
            data = open(join(data_path, file)).read()
            json_data = loads(data)
            config = loads(open(join(data_path, 'conf.json'), 'r').read())
            hook = gitlab(json_data)
            json = {}
            json.update({'token': config['gitlab_token']})
            json.update({'port': config['nginx_port']})
            json.update({'vhost_path': config['vhost_path']})
            json.update({'ssh_url': hook.ssh_url})
            json.update({'http_url': hook.http_url})
            json.update({'repo_name': hook.repo_name})
            json.update({'branch_name': hook.branch_name})
            json.update({'index_id': hook.index_id})
            json.update({'object_id': hook.object_id})
            json.update({'project_id': hook.project_id})
            json.update({'state': hook.state})
            args_json = loads(hook.get_exe_action(action, config)[1])
            checked = []
            for key in args_json.keys():
                checked.append(key)
                expect(args_json[key]).to(
                    equal(json.get(key, '{} Not found'.format(key)))
                )
            for key in json.keys():
                expect(checked).to(contain(key))

with description('GitLab Utils'):
    # clone_on_dir
    with context('Clone on Dir'):
        with it('Must return a String and a returncode == 0 with the '
                'right params(mocked)'):
            with patch("hookshub.hooks.gitlab.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['All Ok\n', '']
                popen_mock.returncode = 0
                popen.return_value = popen_mock
                log, result, err = util.clone_on_dir(
                    'directory', 'branch', 'repository', 'gitlab url'
                )
                expect(len(log) > 0).to(equal(True))
                expect(len(err)).to(equal(0))
                expect(result).to(equal(0))
                popen.stop()

        with it('Must return a String and a returncode != 0 with the '
                'wrong params(mocked)'):
            with patch("hookshub.hooks.gitlab.Popen") as popen:
                popen.start()
                popen_mock = Mock()
                popen_mock.communicate.return_value = ['Not Ok\n', 'Mocked!']
                popen_mock.returncode = 1
                popen.return_value = popen_mock
                log, result, err = util.clone_on_dir(
                    'directory', 'branch', 'repository', 'gitlab url'
                )
                expect(len(log) > 0).to(equal(True))
                expect(len(err) > 0).to(equal(True))
                expect(result).to(equal(1))
                popen.stop()

    # post_comment_pr
    with context('Post Comment On PR'):
        with it('Must return a 201 status code if all OK (Mocked)'):
            with patch("hookshub.hooks.gitlab.requests.post") as req_get:
                req_get.start()

                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)

                req_get.return_value = MockedReturn(201, [])
                code, log = util.post_comment_mr(
                    'URL', 'Token', 1, 12, 'Comment'
                )
                expect(code).to(equal(201))
                req_get.stop()
                
        with it('Must return a error code if status code != 201 (Mocked)'):
            with patch("hookshub.hooks.gitlab.requests.post") as req_get:
                req_get.start()


                class MockedReturn:
                    def __init__(self, status_code, text):
                        self.status_code = status_code
                        self.text = dumps(text)


                req_get.return_value = MockedReturn(400, [])
                code, log = util.post_comment_mr(
                    'URL', 'Token', 1, 12, 'Comment'
                )
                expect(code).to(equal(400))
                req_get.stop()

        with it('Must raise an internal error if a connection exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.gitlab.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = requests.ConnectionError('Mocked Error')
                code, log = util.post_comment_mr(
                    'URL', 'Token', 1, 12, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()

        with it('Must raise an internal error if a http exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.gitlab.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = requests.HTTPError('Mocked Error')
                code, log = util.post_comment_mr(
                    'URL', 'Token', 1, 12, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()

        with it('Must raise an internal error if a request exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.gitlab.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = requests.RequestException('Mocked Error')
                code, log = util.post_comment_mr(
                    'URL', 'Token', 1, 12, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()

        with it('Must raise an internal error if an internal exception'
                ' is thrown (Mocked)'):
            with patch("hookshub.hooks.gitlab.requests.post") as req_get:
                req_get.start()
                req_get.side_effect = Exception('Mocked Error')
                code, log = util.post_comment_mr(
                    'URL', 'Token', 1, 12, 'Comment'
                )
                expect(code).to(equal(0))
                req_get.stop()
