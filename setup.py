#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/27 20:46
# version: python 37

from distutils.core import setup
from setuptools import find_packages

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setup(
    name='coords_transform',
    version='0.0.2-20200407',
    packages = find_packages(),  # 查找包的路径
    include_package_data=True,
    author='Uncle Xiang',
    author_email='tuxgis@126.com',
    url='https://github.com/tuxiang-hub/coords_transform',
    description='A Python module for transforming coordinates.',
    #long_description=open('README.rst').read(),
    install_requires = ["shapely","gdal"],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],

)
