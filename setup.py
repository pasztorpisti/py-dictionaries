# -*- coding: utf-8 -*-

import os
import re
import codecs
from setuptools import setup


script_dir = os.path.dirname(os.path.abspath(__file__))


def read_text_file(path):
    with codecs.open(path, 'r', 'utf-8') as f:
        return f.read()


def find_version(*path):
    contents = read_text_file(os.path.join(script_dir, *path))

    # The version line must have the form
    # version_info = (X, Y, Z)
    m = re.search(
        r'^version_info\s*=\s*\(\s*(?P<v0>\d+)\s*,\s*(?P<v1>\d+)\s*,\s*(?P<v2>\d+)\s*\)\s*$',
        contents,
        re.MULTILINE,
    )
    if m:
        return '%s.%s.%s' % (m.group('v0'), m.group('v1'), m.group('v2'))
    raise RuntimeError('Unable to determine package version.')


setup(
    name='dictionaries',
    version=find_version('src', 'dictionaries.py'),
    description='Dict implementations with attribute access: ReadonlyDictProxy, '
                'FrozenDict, FrozenOrderedDict, Dict, OrderedDict',
    long_description=read_text_file(os.path.join(script_dir, 'README.rst')),
    keywords='Dict FrozenDict FrozenOrderedDict ReadonlyDictProxy '
             'ordered readonly frozen proxy attribute access',

    url='https://github.com/pasztorpisti/py-dictionaries',

    author='István Pásztor',
    author_email='pasztorpisti@gmail.com',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    py_modules=['dictionaries'],
    package_dir={'': 'src'},

    test_suite='tests',
    tests_require=['six'],
)
