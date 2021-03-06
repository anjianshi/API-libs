#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import api_libs

setup(
    name='API-libs',
    version=api_libs.__version__,
    url='https://github.com/anjianshi/api-libs',
    license='MIT',
    author='anjianshi',
    author_email='anjianshi@gmail.com',
    description="一套灵活的组件，帮助你快速搭建起一个 API 系统",
    packages=['api_libs', "api_libs.adapters", "api_libs.parameters"],
    zip_safe=False,
    platforms='any',
    keywords=['api', 'tornado'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
