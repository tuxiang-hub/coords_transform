#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/19 17:09
# version: python 37

from osgeo import gdal,osr
import os,sys
from . import public_func
from . import coords_transform

class ImageTransform(public_func.PublicFuncImage,coords_transform.CoordTrans):
    def __init__(self):
        super(ImageTransform, self).__init__()

    def coordinate_system_conversion_img(self,src_dataset, dst_dataset, dst_sr="EPSG:4326"):
        ds, sr, rows, cols, geotransform = self._read_image(src_dataset)
        gdal.Warp(dst_dataset, ds, format="GTiff", srcSRS=sr, dstSRS=dst_sr)

    def image_transform(self, src_dataset, dst_dataset,transform_method,interval=1000,nodata = None):
        '''
        根据影像的行列号及对应坐标，对影像进行偏移
        :param inImage: 输入影像路径
        :param outImage: 输入影像路径
        :param list_col_row: 行列号的列表（元组）
        :param list_xy: xy坐标的列表（元组
        :return: 无返回值
        '''
        ds, sr, rows, cols, geotransform = self._read_image(src_dataset)

        osr_ds_obj = osr.SpatialReference()
        osr_ds_obj.ImportFromWkt(sr)

        osr_wgs84_obj = osr.SpatialReference()
        osr_wgs84_obj.SetWellKnownGeogCS("WGS84")
        judge = osr_wgs84_obj.IsSame(osr_ds_obj)
        # print(judge)
        if judge == 1:
            col_row_list = self._get_col_row(cols, rows,interval)
            WGS84_xy_list = self._caculate_xy_by_col_row(geotransform, col_row_list)
            new_xy_list = []
            if transform_method == 'g2b':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.gcj02_to_bd09(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            elif transform_method == 'b2g':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.bd09_to_gcj02(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            elif transform_method == 'w2g':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.wgs84_to_gcj02(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            elif transform_method == 'g2w':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.gcj02_to_wgs84(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            elif transform_method == 'b2w':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.bd09_to_wgs84(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            elif transform_method == 'w2b':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.wgs84_to_bd09(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            elif transform_method == 'w2b_bdapi':
                for i in range(len(WGS84_xy_list)):
                    new_xy_list.append(self.wgs84_to_bd09_from_bdapi(WGS84_xy_list[i][0], WGS84_xy_list[i][1]))
            else:
                print('Usage: transform_method must be in one of g2b, b2g, w2g, g2w, b2w, w2b, w2b_bdapi')
                sys.exit()

            coordlist = []
            if len(col_row_list) == len(new_xy_list):
                #print("构建GCPs列表......")
                for i in range(len(new_xy_list)):
                    coordlist.append(gdal.GCP(new_xy_list[i][0], new_xy_list[i][1], 0, col_row_list[i][0], col_row_list[i][1]))

                # 根据脚点坐标进行配准
                #print("为影像写入GCPs......")
                filepath,filename = os.path.split(dst_dataset)
                temp_out = filepath+"/translate.tif"
                gdal.Translate(temp_out,src_dataset, GCPs=coordlist,callback=gdal.TermProgress_nocb)
                #print("终极变换！")
                gdal.Warp(dst_dataset,temp_out, format="GTiff", dstNodata=nodata, dstSRS="EPSG:4326",callback=gdal.TermProgress_nocb)
                os.remove(temp_out)
            else:
                print("Error: convert error! ")
        else:
            print('Error: The data coordinate systemtype must be WGS84')
            sys.exit()

