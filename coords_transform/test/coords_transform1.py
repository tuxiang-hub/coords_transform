#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/19 17:08
# version: python 

import public_func

class CoordTrans(public_func.PublicFuncCoord):
    def __init__(self):
        super(CoordTrans, self).__init__()
        pass
    '''
    def __init__(self):
        super(CoordTrans, self).__init__()
        pass
    '''

    def wgs84_to_gcj02(self,lng, lat):
        """
        WGS84转GCJ02(火星坐标系)
        :param lng:WGS84坐标系的经度
        :param lat:WGS84坐标系的纬度
        :return:
        """
        return self._wgs84_to_gcj02(lng,lat)

    def gcj02_to_bd09(self,lng, lat):
        """
        火星坐标系(GCJ-02)转百度坐标系(BD-09)
        谷歌、高德——>百度
        :param lng:火星坐标经度
        :param lat:火星坐标纬度
        :return:
        """
        return self._gcj02_to_bd09(lng,lat)

    def wgs84_to_bd09(self,lon, lat):
        return self._wgs84_to_bd09(lon, lat)

    def gcj02_to_wgs84(self,lng, lat):
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系的经度
        :param lat:火星坐标系纬度
        :return:
        """
        return self._gcj02_to_wgs84(lng,lat)

    def bd09_to_gcj02(self, bd_lon, bd_lat):
        """
        百度坐标系(BD-09)转火星坐标系(GCJ-02)
        百度——>谷歌、高德
        :param bd_lat:百度坐标纬度
        :param bd_lon:百度坐标经度
        :return:转换后的坐标列表形式
        """
        return self._bd09_to_gcj02(bd_lon,bd_lat)

    def bd09_to_wgs84(self, bd_lon, bd_lat):
        return self._bd09_to_wgs84(bd_lon, bd_lat)

    def wgs84_to_bd09_from_bdapi(self, lon, lat, ak):
        return self._wgs84_to_bd09_from_bdapi(lon,lat,ak)