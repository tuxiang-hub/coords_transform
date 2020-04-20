#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/19 17:11
# version: python 37

from . import public_func

class VectorTransform(public_func.PublicFuncVector):
    def __init__(self):
        super(VectorTransform, self).__init__()


    def coordinate_system_conversion_vector(self, src_dataset, dst_dataset, src_sr, dst_sr):
        self._coordinate_system_conversion_vector(src_dataset, dst_dataset, src_sr, dst_sr)


    def vector_transform(self,src_file, dst_file, transform_method, format="shp"):
        '''

        :param src_file:
        :param dst_file:
        :param transform_method:
        :param format:
        :return:
        '''
        self._vector_transform(src_file,dst_file,transform_method,format)
