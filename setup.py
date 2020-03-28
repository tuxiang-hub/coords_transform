#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/27 20:46
# version: python 37

from distutils.core import setup
from setuptools import find_packages

setup(
    name='coords_transform',
    version='0.1',
    author='Uncle Xiang',
    author_email='tuxgis@126.com',
    url='https://github.com/tuxiang-hub/coords_transform',
    packages=['gdal','shapely','json','sys'],
    description='A Python module for transforming coordinates.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)
