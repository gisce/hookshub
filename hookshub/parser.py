# -*- coding: utf-8 -*-
from hookshub.hooks.github import GitHubWebhook as github
from hookshub.hooks.gitlab import GitLabWebhook as gitlab
from multiprocessing import Pool
from osconf import config_from_environment
from hookshub.hooks.webhook import webhook
from subprocess import Popen, PIPE
from os.path import join
import json
import tempfile
import shutil
import logging


class TempDir(object):
    def __init__(self):
        self.dir = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir)


def run_action(action, hook, conf):
    logger = logging.getLogger('__main__')
    import os
    pid = os.getpid()
    logger.error('[ASYNC({})]Running: {} - {}'.format(pid, action, hook.event))
    args = hook.get_exe_action(action, conf)
    with TempDir() as tmp:
        tmp_path = join(tmp.dir, action)
        with open(tmp_path, 'w') as tmp_json:
            tmp_json.write(args[1])
        args[1] = tmp_path
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        logger.error('[{}]:ProcOut:\n{}'.format(
            action, stdout.replace('|', '\n')
        ))
        logger.error('[{}]:ProcErr:\n{}'.format(
            action, stderr.replace('|', '\n')
        ))
        if proc.returncode != 0:
            logger.error('[{0}]:Failed!\n'.format(
                action
            ))
        else:
            logger.error('[{0}]:Success!\n'.format(
                action
            ))
    return stdout, stderr, proc.returncode, pid


def log_result(res):
    stdout, stderr, returncode, pid = res
    logger = logging.getLogger('__main__')
    if returncode == 0:
        result = 'Success!'
    else:
        result = 'Failure!'
    logger.error('[ASYNC({})] Result: {}'.format(
        pid, result
    ))


class HookParser(object):
    def __init__(self, payload_file, event, pool=Pool(1)):
        self.event = event
        self.payload = {}
        with open(payload_file, 'r') as jsf:
            self.payload = json.loads(jsf.read())
        import logging
        self.logger = logging.getLogger('__main__')
        self.pool = pool

    @staticmethod
    def instancer(payload):
        if 'object_kind' in payload.keys():
            return gitlab(payload)
        elif 'hook' in payload.keys():
            return webhook(payload)
        else:
            return github(payload)

    def run_event_actions(self, config_file):
        timeout = 2
        log = ''
        
        with open(config_file, 'r') as config:
            def_conf = json.loads(config.read())

        if not 'nginx_port' in def_conf.keys():
            def_conf.update({'nginx_port': '80'})
            
        conf = config_from_environment('HOOKSHUB', [
            'github_token', 'gitlab_token', 'vhost_path', 'nginx_port'
        ], **def_conf)

        hook = self.instancer(self.payload)
        i = 0

        if self.logger:
            self.logger.error('Executing {} actions for event: {}\n'.format(
                len(hook.event_actions), hook.event
            ))
        for action in hook.event_actions:
            i += 1
            if self.logger:
                self.logger.error('[Running: <{0}/{1}> - {2}]\n'.format(
                    i, len(hook.event_actions), action)
                )
            proc = self.pool.apply_async(
                run_action, args=(action, hook, conf),
                callback=log_result
            )
            proc.wait(timeout=timeout)
            if proc.ready():
                stdout, stderr, returncode, pid = proc.get()
            else:
                stdout = stderr = 'Still running async, but answering.' \
                                  ' Check log for detailed result...'
                self.logger.error('[{}]:{}'.format(action, stderr))
                returncode = 0

            output = ''
            output += ('[{0}]:ProcOut:\n{1}'.format(
                action, stdout
            ))
            output += ('[{0}]:ProcErr:\n{1}'.format(
                action, stderr
            ))
            if returncode and returncode != 0:
                log += ('[{0}]:{1}\n[{0}]:Failed!\n'.format(
                    action, output
                ))
                return -1, log
            log += ('[{0}]:{1}\n[{0}]:Success!\n'.format(
                action, output
            ))

        return 0, log
