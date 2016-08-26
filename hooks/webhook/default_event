#!/usr/bin/python
# -*- coding: utf-8 -*-
from json import loads
import sys

# Carrega dels arguments. Conte els detalls del event
def arguments():
    payload = loads(sys.argv[1])
    event = sys.argv[2]
    return payload, event

payload, event = arguments()

print ' Default event:'
print '[Default] JSON Data [hook]: {}'.format(payload['hook'])
print '[Default] Event: {}'.format(event)

exit(0)
