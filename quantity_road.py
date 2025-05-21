import pickle
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
import h3
from pp_enum import *
import tqdm

class QuantityRoad:

    def extract_line_segments(shapefile_path):
        """
        提取线状矢量文件中所有线段的起止点坐标
        :param shapefile_path: SHP文件路径
        :return: 三维坐标数组 [[[lat1,lon1],[lat2,lon2]],...]
        """
        # 读取矢量文件
        gdf = gpd.read_file(shapefile_path)
        
        segments = []
        
        # 遍历每个几何要素
        for geom in gdf.geometry:
            # 处理多线段类型
            if isinstance(geom, MultiLineString):
                lines = geom.geoms
            else:
                lines = [geom]
            
            # 提取所有线段
            for line in lines:
                # 获取坐标序列（格式：[ (lon, lat), ... ]）
                coords = list(line.coords)
                
                # 遍历生成线段对
                for i in range(len(coords)-1):
                    # 转换为 [[lat, lon], [lat, lon]] 格式
                    start = (coords[i][1], coords[i][0])  # 交换经纬度顺序
                    end = (coords[i+1][1], coords[i+1][0])
                    segments.append([start, end])
        
        return segments
    def quantity_road(map, shapefile_path):
        """
        量化道路
        :param line_segments: 线段列表 [[[lat1,lon1],[lat2,lon2]],...]
        :param map: 地图对象
        :return: None
        """
        # 提取所有线段
        line_segments = QuantityRoad.extract_line_segments(shapefile_path)
        # 遍历线段，获取这个线状矢量文件中所有线段所跨越的所有单元索引
        road_cellindex_set = set()
        for line in line_segments:
            start_index = h3.geo_to_h3(line[0][0], line[0][1], 11) # TODO：这里写死了，可以用枚举类来代替（分辨率统一），或者用入参（分辨率不统一）
            end_index = h3.geo_to_h3(line[1][0], line[1][1], 11)
            index_set = h3.h3_line(start_index, end_index)
            road_cellindex_set.update(index_set)
        # 匹配map中的单元索引，修改cell的道路拓扑属性
        for h3_index in tqdm.tqdm(road_cellindex_set, desc="量化道路："):
            if h3_index in map.cells:
                cell = map.cells[h3_index]
                cell.road_topology_type = RoadTopologyType.CONNECTEDWAY.value  # TODO：默认先设置为可穿越的道路

# 使用示例
if __name__ == "__main__":
    with open('data/玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    shp_path = "/home/cc/mydata/road_shp/road.shp"
    QuantityRoad.quantity_road(map, shp_path)
    # 保存量化后的地图对象
    with open('data/玄武区.bin', 'wb') as f:
        pickle.dump(map, f)
    