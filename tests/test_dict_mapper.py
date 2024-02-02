import json
import os
import re
import sys
import time
import unittest

import dict_mapper.utils
from dict_mapper import utils

from dict_mapper.dict_mapper import dict_mapper

# Set the timezone on POSIX systems. Need to manually set for Windows tests
if not sys.platform.startswith('win32'):
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()


class MyTests(unittest.TestCase):

    def xtest_utils_dict_mapper_empty_options(self):
        self.assertEqual(dict_mapper({'a': 'abcd'}, {}), {'a': 'abcd'})

    @staticmethod
    def test_utils_dict_mapper_dict():
        raw_output = {
            'A_change': 'A',
            'BCDE_change': 'B',
            'version': '1.1',
            'http': "HTTP/1.1 200 OK",
            'http-update': "HTTP/1.1 200 OK",
            'Status-Code': '200',
            'CamelCaseCase': 'CamelCase',
            'status_reason': 'OK',
            'replace_this_key': 'text',
            'some_numbers': '1343',
            'item_matcher': 'this is the text',
            'Filesystem Created': '2024-02-02T12:00:00Z',
            'Last Mount Time': '2024-02-02T12:00:00Z',
        }

        matcher = re.compile(r'^HTTP/(?P<version>\d+(\.\d+)?) (?P<status_code>\d+)(?: (?P<status_reason>.+))?$')

        def item_mapper(key, value):
            return "{key}: {value}".format(key=key, value=value).lower()

        mapper_config = {
            'value_mapper': {
                'SOME_NUMBERS': 'utils.convert_to_int',
                '.+_change$': lambda x: 'changed to '+x.lower(),
                '*': lambda x: x.upper(),
            },
            'key_mapper': {
                'replace_this_key': 'replaced_key',
                '^Camel.+$': utils.camel_to_snake,
                'version': 'HTTP-Version',
                'status_code': 'Status-Code',
                'status_reason': 'Status-Reason',
                '*': [
                    lambda x: x.lower(),
                    lambda x: x.replace('-', '_'),
                    lambda x: x.replace(' ', '_')
                ],
            },
            'item_mapper': {
                'ITEM_MATCHER': item_mapper,
                # TODO '*:first_match': matcher
                'HTTP': matcher,
            },
            'update_mapper': {
                'http-update': matcher,
            },
        }

        result = dict_mapper(raw_output, mapper_config)
        print()
        print(json.dumps(raw_output, indent=4))
        print()
        print(json.dumps(result, indent=4))

    @staticmethod
    def xtest_utils_dict_mapper_list_dict():
        raw_output = [
            {
                'version': '1.1',
                'StatusCode': '200',
                'status_reason': 'OK',
                'filesystem_created': '2024-02-02T12:00:00Z',
                'last_mount_time': '2024-02-02T12:00:00Z',
            },
            {
                'version': '2',
                'StatusCode': '301',
                'status_reason': 'Moved Permanently',
                'filesystem_created': '2024-02-02T12:00:00Z',
                'last_mount_time': '2024-02-02T12:00:00Z',
            }
        ]

        matcher = re.compile(r'^HTTP/(?P<version>\d+(\.\d+)?) (?P<status_code>\d+)(?: (?P<status_reason>.+))?$')

        mapper_config = {
            'value_mapper': {
                '*': lambda x: x.upper(),
            },
            'key_mapper': {
                '*': [lambda x: x.upper(), lambda x: x.upper()],

            },
            'item_mapper': {
                '*': matcher,
            },
        }
        result = dict_mapper(raw_output, mapper_config)
        print(result)


if __name__ == '__main__':
    unittest.main()
