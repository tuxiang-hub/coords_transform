#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/19 17:11
# version: python 37

import sys,json
from tqdm import tqdm
from osgeo import ogr,gdal
from shapely.geometry import asShape
import public_func
import coords_transform

class VectorTransform(public_func.PublicFuncVector,coords_transform.CoordTrans):
    def __init__(self):
        super(VectorTransform, self).__init__()

    def _judge_vector_type(self,geom_type,WGS84_xy_list,func):
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
        WGS84_xy_list = coord_json['coordinates']
        geom_type = coord_json['type']
        if transform_method == 'g2b':
            self._judge_vector_type(geom_type, WGS84_xy_list, self.gcj02_to_bd09)
        elif transform_method == 'b2g':
            self._judge_vector_type(geom_type,WGS84_xy_list,self.bd09_to_gcj02)
        elif transform_method == 'w2g':
            self._judge_vector_type(geom_type,WGS84_xy_list,self.wgs84_to_gcj02)
        elif transform_method == 'g2w':
            self._judge_vector_type(geom_type,WGS84_xy_list,self.gcj02_to_wgs84)
        elif transform_method == 'b2w':
            self._judge_vector_type(geom_type,WGS84_xy_list,self.bd09_to_wgs84)
        elif transform_method == 'w2b':
            self._judge_vector_type(geom_type,WGS84_xy_list,self.wgs84_to_bd09)
        elif transform_method == 'w2b_bdapi':
            self._judge_vector_type(geom_type,WGS84_xy_list,self.wgs84_to_bd09_from_bdapi)
        else:
            print('Usage: transform_method must be in one of g2b, b2g, w2g, g2w, b2w, w2b, w2b_bdapi')
            sys.exit()

    def vector_transform(self,src_file,dst_file,transform_method,format="shp"):
        ogr.RegisterAll()
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        ds = ogr.Open(src_file, 0)
        if ds is None:
            print('Error: Could not open {}'.format(src_file))
            sys.exit(1)
        layer = ds.GetLayer()  # shp默认是一个layer
        if layer == None:
            print("Error: The layer did not open correctly!")
            sys.exit(1)
        sr = layer.GetSpatialRef()
        #judge = self._judeg_isornot_wgs84(sr)
        judge = 1
        print("judge:", judge)
        if judge == 1:
            print(type(layer))
            print("读取完毕！")
            geom_type = layer.GetGeomType()#图层几何类型
            print("geomtype",geom_type)
            sr = layer.GetSpatialRef()
            #创建输出的layer
            print("开始创建数据源")
            outds,outlayer = self._write_vector(dst_file,geom_type,sr)
            print("创建数据源完毕！")
            '''属性表结构获取与创建'''
            oDefn = layer.GetLayerDefn()
            iFieldCount = oDefn.GetFieldCount()#字段个数
            for i in range(iFieldCount):
                field_obj = oDefn.GetFieldDefn(i)
                (fieldname,fieldtype,fieldlength)=self._get_attribute_fieldname(field_obj)
                print(fieldname,fieldtype,fieldlength)
                self._set_attribute_fieldname(outlayer, fieldname, fieldtype,fieldlength)#输出图层的属性表结构创建

            feature_count = layer.GetFeatureCount()
            print("总计要素数目：",feature_count)
            outfeatureddefn = outlayer.GetLayerDefn()
            for j in tqdm(range(feature_count)):
                #print("j: ",j)
                feature = layer.GetFeature(j)
                geom = feature.GetGeometryRef()  # wktvalue的字符串
                wkt_json = json.loads(geom.ExportToJson())#json格式字符串
                #field_count = feature.GetFieldCount()
                #fieldlist = feature.GetFieldAsString(1)
                #print("fieldlist",fieldlist)
                #print(feature.ExportToJson())
                #print(dir(feature))
                #field_items = feature.items()
                #print(field_items)
                '''计算wkt坐标的偏转'''
                self._vector_coord_transform(wkt_json, transform_method)
                new_geom = asShape(wkt_json)
                shape = ogr.CreateGeometryFromWkt(str(new_geom))
                outfeature = ogr.Feature(outfeatureddefn)
                outfeature.SetFrom(feature)
                outfeature.SetGeometry(shape)
                outlayer.CreateFeature(outfeature)
            outds.Destroy()


VectorTransform_class = VectorTransform()
inpath = r"E:\HN_Image\矢量数据偏移\常德1-2月土地执法数据GCJ02\所有监测图斑WGS84.shp"
outpath = r"E:\HN_Image\矢量数据偏移\常德1-2月土地执法数据GCJ02\所有监测图斑GCJ02.shp"
VectorTransform_class.vector_transform(inpath,outpath,"w2g")