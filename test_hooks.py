# -*- coding: utf-8 -*-
from os.path import abspath, normpath, dirname, join, isfile
from os import listdir
from subprocess import Popen, PIPE
from json import loads


def get_hook_data(hook):
    test_data_path = join(path, 'test_data/{}'.format(hook))
    res_data = []
    for event in listdir(test_data_path):
        with open(join(test_data_path, event), 'r') as data:
            # If exists and can be readed
            res_data.append((join(test_data_path, event), event))
    return res_data


def test_hooks():
    for hook in get_hooks():
        if hook in hooks.keys():
            events = hooks.get(hook)
        else:
            print ('No test data for {}'.format(hook))
            continue
        for data, event in events:
            proc = Popen(
                [get_hook(hook), str(data), event, '--test'],
                stdout=PIPE, stderr=PIPE
            )
            out, err = proc.communicate()
            print (out)
            print (err)
            if proc.returncode != 0:
                print (
                    'Failed test on hook: "{0}" | With event: "{1}"'.format(
                        hook, event
                    )
                )
                exit(-1)
            else:
                print (
                    'Successful test on hook: "{0}" | With event: "{1}"'.format(
                        hook, event
                    )
                )


def get_hook(hook):
    return join(hook_path, hook)


def get_hooks():
    return [
        hook
        for hook in listdir(hook_path)
        if isfile(join(hook_path, hook))
        ]


path = normpath(abspath(dirname(__file__)))
hook_path = join(path, 'hooks')
hooks = {
    'github': get_hook_data('github'),
    'webhook.py': get_hook_data('webhook'),
}
test_hooks()
print ('All test successful')
exit(0)
