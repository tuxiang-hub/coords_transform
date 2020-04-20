#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/20 17:02
# version: python 37

import math,sys,os,json
from osgeo import gdal,osr,ogr
from urllib.request import urlopen
from shapely.geometry import asShape
from tqdm import tqdm


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

    def _wgs84_to_gcj02(self,lng, lat):
        """
        WGS84转GCJ02(火星坐标系)
        :param lng:WGS84坐标系的经度
        :param lat:WGS84坐标系的纬度
        :return:
        """
        if self._out_of_china(lng, lat):  # 判断是否在国内
            return [lng, lat]
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return (mglng, mglat)

    def _gcj02_to_bd09(self,lng, lat):
        """
        火星坐标系(GCJ-02)转百度坐标系(BD-09)
        谷歌、高德——>百度
        :param lng:火星坐标经度
        :param lat:火星坐标纬度
        :return:
        """
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * self.x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * self.x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return (bd_lng, bd_lat)

    def _wgs84_to_bd09(self,lon, lat):
        lon_gcj, lat_gcj = self._wgs84_to_gcj02(lon, lat)
        return self._gcj02_to_bd09(lon_gcj, lat_gcj)

    def _gcj02_to_wgs84(self,lng, lat):
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系的经度
        :param lat:火星坐标系纬度
        :return:
        """
        if self._out_of_china(lng, lat):
            return [lng, lat]
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return (lng * 2 - mglng, lat * 2 - mglat)

    def _bd09_to_gcj02(self, bd_lon, bd_lat):
        """
        百度坐标系(BD-09)转火星坐标系(GCJ-02)
        百度——>谷歌、高德
        :param bd_lat:百度坐标纬度
        :param bd_lon:百度坐标经度
        :return:转换后的坐标列表形式
        """
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * self.x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * self.x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return (gg_lng, gg_lat)

    def _bd09_to_wgs84(self, bd_lon, bd_lat):
        lon, lat = self._bd09_to_gcj02(bd_lon, bd_lat)
        return self._gcj02_to_wgs84(lon, lat)

    def _wgs84_to_bd09_from_bdapi(self, lon, lat, ak):
        data = str(lon) + ',' + str(lat)
        output = 'json'
        url = 'http://api.map.baidu.com/geoconv/v1/?coords=' + data + '&from=1&to=5&output=' + output + '&ak='+ak
        req = urlopen(url)
        res = req.read().decode()
        temp = json.loads(res)
        baidu_x = 0
        baidu_y = 0
        if temp['status'] == 0:
            baidu_x = temp['result'][0]['x']
            baidu_y = temp['result'][0]['y']

        return (baidu_x, baidu_y)

class PublicFunc(object):
    def _judeg_isornot_wgs84(self,in_sr):
        '''
        判断输入的数据集是否是WGS84坐标系，矢量栅格公用
        :param in_sr: 输入的坐标系
        :return: 返回判断结果
        '''
        osr_ds_obj = osr.SpatialReference()
        osr_ds_obj.ImportFromWkt(str(in_sr))
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
        '''

        :param inImage:
        :return:
        '''
        ds = gdal.Open(inImage)
        sr = ds.GetProjectionRef()
        rows = ds.RasterYSize
        cols = ds.RasterXSize
        geotransform = ds.GetGeoTransform()
        return ds,sr,rows,cols,geotransform

class PublicFuncVector(PublicFuncCoord,PublicFunc):
    def _coordinate_system_conversion_vector(self, src_dataset, dst_dataset, src_sr, dst_sr):
        '''
        矢量数据的坐标转换
        :param src_dataset:输入数据
        :param dst_dataset:输出数据
        :param src_sr:格式为"EPSG:4212"
        :param dst_sr:格式为"EPSG:4326"
        :return:
        '''
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
        gdal.VectorTranslate(src_dataset, dst_dataset, srcSRS=src_sr, dstSRS=dst_sr)
    '''
    def _read_vector(self,src_file):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
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
    '''

    def _get_attribute_fieldname(self,in_fieldobject):
        '''
        获取图层的表结构（属性表的字段名称、字段类型、字段长度）
        :param in_fieldname: 字段表结构对象
        :return: tuple=(属性表的字段名称、字段类型、字段长度)
        '''
        return (in_fieldobject.GetNameRef(),in_fieldobject.GetType(),in_fieldobject.GetWidth())

    def _write_vector(self, dst_file, geom_type, spatial_reference):
        '''

        :param dst_file:
        :param geom_type:
        :param spatial_reference:
        :return:
        '''
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

    def _judge_vector_type(self,geom_type,WGS84_xy_list,func):
        '''

        :param geom_type:
        :param WGS84_xy_list:
        :param func:
        :return:
        '''
        if geom_type == "Point":
            WGS84_xy_list[0],WGS84_xy_list[1] = func(WGS84_xy_list[0],WGS84_xy_list[1])
        elif geom_type == "MultiPoint" or geom_type == "LineString":
            for i in range(len(WGS84_xy_list)):
                WGS84_xy_list[i][0], WGS84_xy_list[i][1] = func(WGS84_xy_list[i][0], WGS84_xy_list[i][1])
        elif geom_type == "Polygon" or geom_type == "MultiLineString":
            for i in range(len(WGS84_xy_list)):
                for j in range(len(WGS84_xy_list[i])):
                    WGS84_xy_list[i][j][0], WGS84_xy_list[i][j][1] = func(WGS84_xy_list[i][j][0], WGS84_xy_list[i][j][1])
        elif geom_type == "MultiPolygon":
            for i in range(len(WGS84_xy_list)):
                for j in range(len(WGS84_xy_list[i])):
                    for k in range(len(WGS84_xy_list[i][j])):
                        WGS84_xy_list[i][j][k][0], WGS84_xy_list[i][j][k][1] = func(WGS84_xy_list[i][j][k][0],
                                                                          WGS84_xy_list[i][j][k][1])
        else:
            print('warning: "{}" This type is not currently supported '.format(geom_type))
            sys.exit(1)

    def _vector_coord_transform(self,coord_json,transform_method):
        '''

        :param coord_json:
        :param transform_method:
        :return:
        '''
        WGS84_xy_list = coord_json['coordinates']
        geom_type = coord_json['type']
        if transform_method == 'g2b':
            self._judge_vector_type(geom_type, WGS84_xy_list, self._gcj02_to_bd09)
        elif transform_method == 'b2g':
            self._judge_vector_type(geom_type,WGS84_xy_list,self._bd09_to_gcj02)
        elif transform_method == 'w2g':
            self._judge_vector_type(geom_type,WGS84_xy_list,self._wgs84_to_gcj02)
        elif transform_method == 'g2w':
            self._judge_vector_type(geom_type,WGS84_xy_list,self._gcj02_to_wgs84)
        elif transform_method == 'b2w':
            self._judge_vector_type(geom_type,WGS84_xy_list,self._bd09_to_wgs84)
        elif transform_method == 'w2b':
            self._judge_vector_type(geom_type,WGS84_xy_list,self._wgs84_to_bd09)
        elif transform_method == 'w2b_bdapi':
            self._judge_vector_type(geom_type,WGS84_xy_list,self._wgs84_to_bd09_from_bdapi)
        else:
            print('Usage: transform_method must be in one of g2b, b2g, w2g, g2w, b2w, w2b, w2b_bdapi')
            sys.exit()

    def _vector_transform(self,src_file,dst_file,transform_method,format="shp"):
        '''

        :param src_file:
        :param dst_file:
        :param transform_method:
        :param format:
        :return:
        '''
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
        ogr.RegisterAll()
        ds = ogr.Open(src_file, 0)
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
            geom_type = oLayer.GetGeomType()  # 图层几何类型
            sr = oLayer.GetSpatialRef()
            # 创建输出的layer
            outds, outlayer = self._write_vector(dst_file, geom_type, sr)
            '''属性表结构获取与创建'''
            oDefn = oLayer.GetLayerDefn()
            iFieldCount = oDefn.GetFieldCount()  # 字段个数
            for i in range(iFieldCount):
                field_obj = oDefn.GetFieldDefn(i)
                (fieldname, fieldtype, fieldlength) = self._get_attribute_fieldname(field_obj)
                self._set_attribute_fieldname(outlayer, fieldname, fieldtype, fieldlength)  # 输出图层的属性表结构创建

            feature_count = oLayer.GetFeatureCount()
            outfeatureddefn = outlayer.GetLayerDefn()
            for j in tqdm(range(feature_count)):
                feature = oLayer.GetFeature(j)
                geom = feature.GetGeometryRef()  # wktvalue的字符串
                wkt_json = json.loads(geom.ExportToJson())  # json格式字符串

                '''计算wkt坐标的偏转'''
                self._vector_coord_transform(wkt_json, transform_method)
                new_geom = asShape(wkt_json)
                shape = ogr.CreateGeometryFromWkt(str(new_geom))
                outfeature = ogr.Feature(outfeatureddefn)
                outfeature.SetFrom(feature)
                outfeature.SetGeometry(shape)
                outlayer.CreateFeature(outfeature)
            outds.Destroy()
        else:
            print("Warning: The coordinate system of sourse vector file is not WGS84!")
            sys.exit(1)


