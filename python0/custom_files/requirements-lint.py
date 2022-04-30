#!/usr/local/bin/python3
# coding=utf-8
from os import path
import sys
import requirements

errors = []

if not (len(sys.argv)-1):
    print('ERROR - Missing Argument')
    exit(1)

req_file = sys.argv[1]
print('Linting {}: '.format(sys.argv[1]))

if not path.exists(req_file):
    print('ERROR - File not found {}'.format(req_file))
    exit(1)

with open(req_file, 'r') as fd:
    for req in requirements.parse(fd):
        if not len(req.specs):
            print('Flag -> {}'.format(req.name))
            errors.append('Requirements Lint Failure - Missing Version for requirement {}'.format(req.name))
        else:
            for spec in req.specs:
                comparation, version = spec
                if comparation != '==':
                    print('Flag -> {}'.format(req.name))
                    errors.append(
                        'Requirements Lint Failure - Fixed version required for requirement {} found {}, required =='.format(
                            req.name,
                            comparation,
                        ))
                else:
                    print('Good -> {}'.format(req.name))

if len(errors):
    for error in errors:
        print(error)
    exit(1)
