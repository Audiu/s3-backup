#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import subprocess
from setuptools.command import easy_install

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


def get_long_description():
    readme_file = 'README.md'
    if not os.path.isfile(readme_file):
        return ''
    # Try to transform the README from Markdown to reStructuredText.
    try:
        easy_install.main(['-U', 'pyandoc==0.0.1'])
        import pandoc
        pandoc.core.PANDOC_PATH = 'pandoc'
        doc = pandoc.Document()
        doc.markdown = open(readme_file).read()
        description = doc.rst
    except Exception:
        description = open(readme_file).read()
    return description


setup(
    name='S3Backup',
    version=version_git,
    author='Mike Goodfellow',
    author_email='mike@mikegoodfellow.co.uk',
    packages=find_packages(),
    url='https://github.com/mgoodfellow/s3-backup',
    license='MIT',
    description='Perform scripted backups to Amazon S3',
    long_description=get_long_description(),
    zip_safe=True,
    install_requires=requirements,
    keywords=['backup', 'aws', 's3'],
)
