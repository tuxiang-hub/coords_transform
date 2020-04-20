#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/4/19 17:35
# version: python 37

from coords_transform import vector_transform

#创建coords_transform.CoordTrans()对象
class_ct = vector_transform.VectorTransform()

class_ct.coordinate_system_conversion_vector(src_dataset, dst_dataset, src_sr, dst_sr)
'''
此函数为对矢量数据进行坐标系转换，支持不同地理坐标系之间的转换，如北京54转WGS84，只不过其精度有限，
凡是牵扯到地理椭球体转换的时候，该函数提供的转换精度有限，如想准确进行不同地理椭球体之间的转换，
请使用三参数或者七参数进行转换。
src_dataset：转换前源数据路径
dst_dataset：转换后输出数据路径
src_sr：源数据坐标系的EPSG代码，格式为:比如WGS84坐标系表示为："EPSG:4326",北京54坐标系表示为："EPSG:4212"
dst_sr：转换的目标坐标系，填写格式如上"EPSG:4326"
'''

class_ct.vector_transform(src_file, dst_file, transform_method, format="shp")
'''
此函数功能是将矢量数据按照不同的方法进行偏移
src_dataset：偏移前的源数据路径
dst_dataset：偏移后的栅格数据路径
transform_method：包含g2b, b2g, w2g, g2w, b2w, w2b, w2b_bdapi等七种方法
format：目前支持两种数据格式，shp和gdb，默认为shp格式
'''