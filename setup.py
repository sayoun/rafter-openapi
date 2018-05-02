"""
Rafter OpenAPI
"""
import codecs
import os
import re
from setuptools import setup


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'rafter_openapi', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name='rafter-openapi',
    version=version,
    url='http://github.com/sayoun/rafter-openapi/',
    license='MIT',
    author='sayoun',
    author_email='sayoun@pm.me',
    description='OpenAPI support for Rafter',
    packages=['rafter_openapi'],
    package_data={'rafter_openapi': ['ui/*']},
    platforms='any',
    install_requires=[
        'rafter',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
