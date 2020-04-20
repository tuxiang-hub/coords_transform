#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/4/19 17:35
# version: python 37

from coords_transform import image_transform

#创建coords_transform.CoordTrans()对象
class_ct = image_transform.ImageTransform()

class_ct.coordinate_system_conversion_img(src_dataset,dst_dataset,dst_sr="EPSG:4326")
'''
此函数为对影像进行坐标系转换，支持不同地理坐标系之间的转换，如北京54转WGS84，只不过其精度有限，
凡是牵扯到地理椭球体转换的时候，该函数提供的转换精度有限，如想准确进行不同地理椭球体之间的转换，
请使用三参数或者七参数进行转换。
src_dataset：转换前源数据路径
dst_dataset：转换后输出数据路径
dst_sr：转换的目标坐标系，该参数默认为WGS84坐标系，当不填写该参数时，默认目标坐标系为WGS84
'''

class_ct.image_transform(src_dataset,dst_dataset,transform_method,interval,nodata)
'''
此函数功能是将栅格数据按照不同的方法进行偏移
src_dataset：偏移前的源数据路径
dst_dataset：偏移后的栅格数据路径
transform_method：包含g2b, b2g, w2g, g2w, b2w, w2b, w2b_bdapi等七种方法
interval：加密点，默认值1000，当你的栅格数据范围过大时，为了提高栅格内部偏移精确度，
因此每隔interval个像素取一个坐标值参与计算转换
nodata：当栅格不规则时，避免出现黑色背景，可设置nodata值来去除黑边
'''