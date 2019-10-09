#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import subprocess


def parse_requirements(filename):
    return list(filter(lambda line: (line.strip())[0] != '#',
                       [line.strip() for line in open(filename).readlines()]))


def calculate_version():
    # Get version from tags and write to version.py.
    # Also, when git in not available, such as PyPi package, use stored version
    version_py = os.path.join(os.path.dirname(__file__), 'version.py')
    try:
        version_git = subprocess.check_output(['git', 'tag']).rstrip().split('\n')[-1]
    except Exception:
        with open(version_py, 'r') as fh:
            version_git = (open(version_py).read()
                           .strip().split('=')[-1].replace('"', ''))
    with open(version_py, 'w') as fh:
        fh.write('__version__= "' + version_git + '"')
    return version_git


requirements = parse_requirements('requirements.txt')
version_git = calculate_version()

setup(
    name='S3Backup',
    version=version_git,
    author='Mike Goodfellow',
    author_email='mdgoodfellow@gmail.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    url='https://github.com/mgoodfellow/s3-backup',
    license='MIT',
    description='Perform scripted backups to Amazon S3',
    long_description=open('README.rst').read(),
    zip_safe=False,
    install_requires=requirements,
    keywords=['backup', 'aws', 's3'],
)
