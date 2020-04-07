# coords_transform
本程序用来坐标转换，包括WGS84坐标和GCJ02/bd09坐标之间的互相转换
<<<<<<< HEAD

本程序坐标转换部分的算法来自：https://github.com/wandergis/coordTransform_py

在以上算法中加入了由百度api和高德api提供的精确从WGS84转为BD09和GCJ02坐标接口调用

=======
本程序坐标转换部分的算法来自：https://github.com/wandergis/coordTransform_py
在以上算法中加入了由百度api和高德api提供的精确从WGS84转为BD09和GCJ02坐标接口调用
>>>>>>> 0df440c7e2918e05994685f0f83596e4691325ea
基于开源GDAL库将以上算法再次封装，实现直接对栅格数据集、矢量数据进行直接坐标互转
