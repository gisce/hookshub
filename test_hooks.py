#!/usr/bin/python
# -*- coding: utf-8 -*-
from json import dumps
from subprocess import Popen, PIPE
from os.path import abspath, normpath, dirname, join

import tempfile
import shutil


class TempDir(object):
    def __init__(self):
        self.dir = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir)

origin = {
    'github': dumps({
        'key': 'value'
    }),
    'gitlab': dumps({
        'key': 'value',
        'object_kind': 'something'
    }),
    'webhook': dumps({
        'key': 'value',
        'hook': 'webhook'
    }),
}

for source in origin:
    print ('Testing Hooks for [{}]:'.format(source))
    with TempDir() as temp_dir:
        tmp_json = join(temp_dir.dir, 'json')
        with open(tmp_json, 'w') as json:
            json.write(origin[source])
        listener_path = join(
            normpath(abspath(dirname(__file__))), 'listener.py'
        )
        proc = Popen([listener_path, tmp_json, '--test'],
                     stderr=PIPE, stdout=PIPE)
        out, err = proc.communicate()
        output = out
        output += err
        if proc.returncode != 0:
            print ('{0}[test:{1}]Failed!\n'.format(output, source))
        print ('{0}[test:{1}]Success!\n'.format(output, source))
