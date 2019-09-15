# -*- coding: utf8 -*-

from distutils.core import setup

setup(
    name='pyfixwidth',
    packages=['fixwidth'],
    version='0.1.1',
    description="Read fixed width data files",
    author='Chris Poliquin',
    author_email='chrispoliquin@gmail.com',
    url='https://github.com/poliquin/pyfixwidth',
    keywords=['data', 'fixed width', 'parse', 'parser'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities'
    ],
    long_description="""\
Read fixed width data files
---------------------------
Python 3 module for reading fixed width data files and converting the field
contents to appropriate Python types.
"""
)
