import geopandas as gpd
import h3
from data_structures import *
from tqdm import tqdm

def generate_road_adjacency_list(shp_file_path, h3_resolution):
    """读取矢量路网,筛选出notpassbale的道路,最后生成矢量路网邻接表"""
    # 读取shp文件
    gdf = gpd.read_file(shp_file_path)
    # 取出所有的线要素
    lines = gdf.geometry[gdf.geometry.type == 'LineString']
    # 整个矢量路网的h3索引数组
    h3_indexes = []
    # 遍历gdf
    for index, row in gdf.iterrows():
        # 检查几何类型是否为线要素
        if row.geometry.type != 'LineString':
            continue
        # 检查fclass属性是否为footway
        if row['fclass'] != 'notpassable':
            continue
        # 单个线要素的h3索引数组
        line_h3_indexes = []
        # 遍历线要素中点的坐标
        for point in row.geometry.coords:
            # 转为h3索引
            h3_index = h3.geo_to_h3(point[1], point[0], h3_resolution)
            # 将索引添加到数组中
            line_h3_indexes.append(h3_index)
        # 将单个线要素的h3索引数组添加到整个矢量路网的h3索引数组中
        h3_indexes.append(line_h3_indexes)

    # 矢量路网邻接表
    road_adjacency_list = {}
    # 遍历h3索引数组
    for line_h3_indexes in h3_indexes:
        # 遍历单个线要素的h3索引
        for i in range(len(line_h3_indexes)):
            # 获取当前h3索引
            current_h3_index = line_h3_indexes[i]
            # 获取上一个h3索引（如果存在）
            last_h3_index = line_h3_indexes[i - 1] if i > 0 else None
            # 获取下一个h3索引（如果存在）
            next_h3_index = line_h3_indexes[i + 1] if i < len(line_h3_indexes) - 1 else None
            # 如果当前h3索引不在邻接表中，则添加；如果在的话就继续在后面添加邻居
            if current_h3_index not in road_adjacency_list:
                road_adjacency_list[current_h3_index] = set()
            # 添加邻居h3索引到当前h3索引的邻接列表中
            if next_h3_index is not None:
                road_adjacency_list[current_h3_index].add(next_h3_index)
            if last_h3_index is not None:
                road_adjacency_list[current_h3_index].add(last_h3_index)
    return road_adjacency_list

def quantity_by_road_adjacency_list(road_adjacency_list, map):
    """根据路网邻接表进行量化"""
    # 遍历邻接表
    for current_index, neighbor_indexes in tqdm(road_adjacency_list.items(), desc="量化不可通行的路网"):
        for neighbor_index in neighbor_indexes:
            line_indexes = h3.h3_line(current_index, neighbor_index)
            # 遍历线上的h3索引
            for line_index in line_indexes:
                if line_index not in map.cells:
                    continue
                map.cells[line_index].is_roadpoint = True
                map.cells[line_index].road_topology_type = RoadTopologyType.ISOLATEDWAY.value

def quantity_junctions(junction_shp, map):
    """量化连接点"""
    # 打开junction_shp
    gdf = gpd.read_file(junction_shp)
    # 遍历gdf
    for index, row in tqdm(gdf.iterrows(), desc="量化连接点", total=len(gdf)):
        # 检查几何类型是否为点要素
        if row.geometry.type != 'Point':
            continue
        # 获取点的坐标
        point = row.geometry.coords[0]
        # 转为h3索引
        h3_index = h3.geo_to_h3(point[1], point[0], GlobalConfig().h3_resolution)
        # 如果h3索引在map中，则设置为连接点
        if h3_index in map.cells:
            map.cells[h3_index].is_junction = True
            map.cells[h3_index].road_topology_type = RoadTopologyType.ACCESSIBLE.value

if __name__ == "__main__":
    road_shp_path = r"/home/cc/mydata/mock_road/mock_road.shp"
    h3_resolution = GlobalConfig().h3_resolution
    road_adjacency_list = generate_road_adjacency_list(road_shp_path, h3_resolution)
    



