#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/19 17:11
# version: python 37

import public_func

class VectorTransform(public_func.PublicFuncVector):
    def __init__(self):
        super(VectorTransform, self).__init__()

    def vector_transform(self,src_file,dst_file,transform_method,format="shp"):
        '''

        :param src_file:
        :param dst_file:
        :param transform_method:
        :param format:
        :return:
        '''
        self._vector_transform(src_file,dst_file,transform_method,format)

VectorTransform_class = VectorTransform()
inpath = r"E:\HN_Image\矢量数据偏移\test\WGS84_.shp"
outpath = r"E:\HN_Image\矢量数据偏移\test\GCJ02_.shp"
VectorTransform_class.vector_transform(inpath,outpath,"w2g")