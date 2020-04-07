#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/19 17:11
# version: python 37

from osgeo import gdal,osr,ogr
from shapely.wkt import dumps, loads
import json,geojson
src_file = r"E:\HN_Image\test\mutilpolygon.shp"
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")
gdal.SetConfigOption("SHAPE_ENCODING","")
ogr.RegisterAll()
ds = ogr.Open(src_file, update = 1)
#print(dir(ds))
print(ds.GetName())
driver = ds.GetDriver()
print(driver.GetName())
#print(dir(driver))
oLayer = ds.GetLayerByIndex(0)
#print(oLayer.GetName())
#ds.CopyLayer(oLayer.GetName(),"test")
#print(oLayer.GetSpatialRef())
print(oLayer.GetFeatureCount())
oDefn = oLayer.GetLayerDefn()#获取图层的属性表结构
iFieldCount = oDefn.GetFieldCount()
print("字段个数",iFieldCount)

#############创建##############
outDriverName = "ESRI Shapefile"
outDriver = ogr.GetDriverByName(outDriverName)
# 创建数据源
outDS = outDriver.CreateDataSource(r"E:\HN_Image\test\boundary_out.shp")
# 创建图层，创建一个多边形图层，这里没有指定空间参考，如果需要的话，需要在这里进行指定
papszLCO = []
outLayer = outDS.CreateLayer("TestPolygon", None, ogr.wkbPolygon, papszLCO)

# 下面创建属性表
# 先创建一个叫FieldID的整型属性
#outFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)
#outLayer.CreateField(outFieldID, 1)
filed_list = []
for iAttr in range(iFieldCount):
    oField = oDefn.GetFieldDefn(iAttr)
    print(oField.GetNameRef(),oField.GetType(),oField.GetFieldTypeName(oField.GetType()), oField.GetWidth(),oField.GetPrecision())
    filed_list.append((oField.GetNameRef(),oField.GetType(),oField.GetFieldTypeName(oField.GetType()), oField.GetWidth(),oField.GetPrecision()))
    outFieldID = ogr.FieldDefn(oField.GetNameRef(), oField.GetType())
    outLayer.CreateField(outFieldID, 1)#创建字段，参数1为兼容设置
outfeatureddefn = outLayer.GetLayerDefn()
feature_list = []
for feature in oLayer:
    dic = {}
    for iField in range(iFieldCount):
        oFieldDefn = oDefn.GetFieldDefn(iField)
        line = " %s (%s) = " % (oFieldDefn.GetNameRef(), ogr.GetFieldTypeName(oFieldDefn.GetType()))

        if feature.IsFieldSet(iField):
            line = line + "%s" % (feature.GetFieldAsString(iField))
            dic.update({oFieldDefn.GetNameRef():feature.GetFieldAsString(iField)})
        else:
            line = line + "(null)"

        #print(line)

    # 获取要素中的几何体
    oGeometry = feature.GetGeometryRef()
    wkt = oGeometry.ExportToJson()
    print(geojson.loads(wkt))
    #dic.update({"wkt": wkt})
    #feature_list.append(dic)

#print(feature_list)
'''
for i in range(len(feature_list)):
    outfeat = ogr.Feature(outfeatureddefn)
    dict = feature_list[i]
    for key in dict:
        if key == "wkt":
            polygon = ogr.CreateGeometryFromWkt(dict[key])
            outfeat.SetGeometry(polygon)
        else:
            outfeat.SetField(key, dict[key])
        #print(feature_list[i][key])
    outLayer.CreateFeature(outfeat)
    
    outfeat.SetGeometry(feature_list[i]['geom'])
    for key in feature_list[i]:
        if key != "geom":
            outfeat.SetField(key, feature_list[i][key])
    
    '''
print("done!!!")
'''
print(dir(oLayer))
print()
print("111",oLayer.GetGeomType())
#filed_defn = oLayer.GetLayerDefn()
#iFieldCount = filed_defn.GetFieldCount()
oFeature = oLayer.GetFeature(0)
#print(dir(oFeature))
geom = oFeature.GetGeometryRef()

#print(geom.ExportToWkt())
wkt2 = "POLYGON ((114.837484008666 28.1090485692271,115.973553274691 28.1090485692271,115.973553274691 27.1502224596923,114.837484008666 27.1502224596923,114.837484008666 28.1090485692271))"
polygon = ogr.CreateGeometryFromWkt(wkt2)
oFeature.SetGeometryDirectly(polygon)

geom = oFeature.GetGeometryRef()
#print(geom.ExportToWkt())
oFeature.Destroy()

for feature in oLayer:
    geom = feature.GetGeometryRef()
    print(type(geom.ExportToJson()))
    geom_json = json.loads(geom.ExportToJson())
    geom_type = geom_json['type']
    geom_coord = geom_json['coordinates']
    print(geom_type)
    print(geom_coord)
    break
'''
'''
wkt = geom.ExportToWkt()
print(wkt)
ss = loads(wkt)
print(ss)
print(ss.exterior.coords[:])
'''