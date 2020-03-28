#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/20 17:02
# version: python 37

import math,sys,os
from osgeo import gdal,osr,ogr

class PublicFuncCoord(object):
    def __init__(self):
        self.x_pi = 3.14159265358979324 * 3000.0 / 180.0
        self.pi = math.pi  # π
        self.ee = 0.00669342162296594323  # 偏心率平方
        # CGCS2000扁率0.00335281068118231893543414612613
        # wgs84扁率0.00335281066474748071984552861852‬
        self.a = 6378245.0  # 长半轴

    def _transformlat(self, lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.pi) + 40.0 *
                math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 *
                math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transformlng(self, lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.pi) + 40.0 *
                math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 *
                math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return ret

    def _out_of_china(self, lng, lat):
        """
        判断是否在国内，不在国内不做偏移
        :param lng:
        :param lat:
        :return:
        """
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

class PublicFunc(object):
    def _judeg_isornot_wgs84(self,in_sr):
        osr_ds_obj = osr.SpatialReference()
        osr_ds_obj.ImportFromWkt(in_sr)
        osr_wgs84_obj = osr.SpatialReference()
        osr_wgs84_obj.SetWellKnownGeogCS("WGS84")
        judge = osr_wgs84_obj.IsSame(osr_ds_obj)
        return judge

class PublicFuncImage(PublicFunc):
    def _get_col_row(self, cols, rows, interval):
        '''
        根据总列数，总行数，间隔值，计算需要加密的行列号，并返回
        :param cols: 栅格总列数
        :param rows: 栅格总行数
        :param interval: 间隔值，默认1000
        :return: 返回一个元组((col1,row1),(col2,row2),(col3,row3)......)
        '''
        col_row_list = []
        if cols % interval != 0:  # 获取最后一列的行列号
            for row in range(0, rows + 1, interval):
                col_row_list.append((cols, row))
        if rows % interval != 0:  # 获取最后一行的行列号
            for col in range(0, cols + 1, interval):
                col_row_list.append((col, rows))
        if rows % interval != 0 and cols % interval != 0:  # 获取（cols，rows）
            col_row_list.append((cols, rows))

        for i in range(0, rows + 1, interval):
            for j in range(0, cols + 1, interval):
                col_row_list.append((j, i))
        return tuple(col_row_list)

    def _caculate_xy_by_col_row(self, geotransform, col_row_tuple):
        '''
        根据行列号计算做对应行列号的坐标，像素左上角的坐标，不是像素中心的坐标
        :param geotransform:gdal获取的数据集六参数
        :param col_row_tuple:列号、行号元组((col1,row1),(col2,row2),(col3,row3)......)
        :return:返回对应行列号的xy元组((x1,y1),(x2,y2),(x3,y3)......)
        '''
        xy_list = []
        for i in range(len(col_row_tuple)):
            x = geotransform[0] + col_row_tuple[i][0] * abs(geotransform[1])
            y = geotransform[3] - col_row_tuple[i][1] * abs(geotransform[5])
            xy_list.append((x, y))
        return tuple(xy_list)

    def _read_image(self, inImage):
        ds = gdal.Open(inImage)
        sr = ds.GetProjectionRef()
        rows = ds.RasterYSize
        cols = ds.RasterXSize
        geotransform = ds.GetGeoTransform()
        return ds,sr,rows,cols,geotransform

class PublicFuncVector(PublicFunc):
    def _read_vector(self,src_file):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        ogr.RegisterAll()
        ds = ogr.Open(src_file,0)
        if ds is None:
            print('Error: Could not open {}'.format(src_file))
            sys.exit(1)
        oLayer = ds.GetLayer()  # shp默认是一个layer
        if oLayer == None:
            print("Error: The layer did not open correctly!")
            sys.exit(1)
        sr = oLayer.GetSpatialRef()
        judge = self._judeg_isornot_wgs84(sr)
        if judge == 1:
            return oLayer
        else:
            print("Warning: The coordinate system of sourse vector file is not WGS84!")
            sys.exit(1)

    def _get_attribute_fieldname(self,in_fieldobject):
        '''
        获取图层的表结构（属性表的字段名称、字段类型、字段长度）
        :param in_fieldname: 字段表结构对象
        :return: tuple=(属性表的字段名称、字段类型、字段长度)
        '''
        return (in_fieldobject.GetNameRef(),in_fieldobject.GetFieldTypeName(in_fieldobject.GetType()),in_fieldobject.GetWidth())

    def _coord_convert_wkt(self,geom_type, coord_list):
        '''
        将geometry类型的字符串及坐标串列表转变为标准的wkt字符串
        :param geom_type: POLYGON,LINE,POINT......
        :param coord_list:[[X,Y],[X,Y],[X,Y],[X,Y]]
        :return:'POLYGON ((X Y,X Y,X Y,X Y))'
        '''
        for i in range(coord_list):
            pass
        pass

    def _write_vector(self, dst_file, geom_type, spatial_reference):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if driver == None:
            print("Error: The driver(ESRI Shapefile) is not available！")
            sys.exit(1)
        datasourse = driver.CreateDataSource(dst_file)
        if datasourse == None:
            print("Error: Create datasourse failed！")
            sys.exit(1)
        dir,filename = os.path.split(dst_file)
        layer = datasourse.CreateLayer(filename[:-3], spatial_reference, geom_type = geom_type)
        if layer == None:
            print("Error: Create layer failed！")
            sys.exit(1)
        return datasourse,layer

    def _set_attribute_fieldname(self, in_layer, fieldname, fieldtype,fieldlength):
        '''
        给图层创建属性字段，创建属性表结构
        :param in_layer:
        :param fieldname:
        :param fieldtype:
        :param fieldlength:
        :return:
        '''
        field = ogr.FieldDefn(fieldname, fieldtype)
        field.SetWidth(fieldlength)
        in_layer.CreateField(field, 1)

