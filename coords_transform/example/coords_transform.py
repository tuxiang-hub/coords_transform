#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/4/19 17:35
# version: python 37

from coords_transform import coords_transform

#创建coords_transform.CoordTrans()对象
class_ct = coords_transform.CoordTrans()

lon = "经度"
lat = "纬度"
#BD09转GCJ02
class_ct.bd09_to_gcj02(lon,lat)
#BD09转WGS84
class_ct.bd09_to_wgs84(lon,lat)
#GCJ02转BD09
class_ct.gcj02_to_bd09(lon,lat)
#GCJ02转WGS84
class_ct.gcj02_to_wgs84(lon,lat)
#WGS84转GCJ02
class_ct.wgs84_to_gcj02(lon,lat)
#WGS84转BD09
class_ct.wgs84_to_bd09(lon,lat)
#基于百度api接口WGS84转BD09
class_ct.wgs84_to_bd09_from_bdapi(lon,lat,ak="xxxxx")

