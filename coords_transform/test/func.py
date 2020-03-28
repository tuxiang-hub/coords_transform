#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/27 18:51
# version: python 

def aaaa(a,b):
    c=a+b
    return c

def bbbb(a ,func):
    d = a + func(3,6)
    print(d)
bbbb(10,aaaa)