import pickle
import h3
from data_structures import *
from pp_enum import *
from quantity_roadnet import *
from pp_strategy import *


def pp(map, start, end, road_adjacency_list=None):
    """
    路径规划
    :param map: 地图对象
    :param start: 起点坐标
    :param end: 终点坐标
    :return: path: 路径对象
    """

    """初始化"""
    # 从0-15分辨率的索引，在map的字典中找出起始点和终点的索引
    start_cell = None
    end_cell = None
    for i in range(0, 16):
        start_index = h3.geo_to_h3(start[0], start[1], i)
        end_index = h3.geo_to_h3(end[0], end[1], i)
        if start_index in map.cells:
            start_cell = map.cells[start_index]
        if end_index in map.cells:
            end_cell = map.cells[end_index]
        if start_cell and end_cell:
            break
    if start_cell is None or end_cell is None:
        raise ValueError("起点或终点不在地图范围内")

    """使用A*算法进行路径规划"""
    # 初始化变量
    open_set = set()  # 待评估的节点集合
    closed_set = set()  # 已评估的节点集合
    path = Map()  # 最终路径
    start_cell.g = 0  # 起点的g值
    for neighbor in start_cell.neighbors:
        if neighbor in map.cells:
            map.cells[neighbor].father = start_cell  # 设置父节点
            map.cells[neighbor].g = start_cell.g + h3.point_dist(start_cell.center, map.cells[neighbor].center)
            map.cells[neighbor].h = h3.point_dist(map.cells[neighbor].center, end_cell.center)
            map.cells[neighbor].f = map.cells[neighbor].g + map.cells[neighbor].h
            open_set.add(map.cells[neighbor])
    closed_set.add(start_cell)
    current_cell = None # 当前节点
    # 开始A*算法
    while open_set:
        # 找到f值最小的节点
        current_cell = min(open_set, key=lambda cell: cell.f)
        # 刷新显示
        print(f"\r距离终点: {current_cell.h:.6f}", end='', flush=True)
        if current_cell == end_cell:
            break  # 找到终点，退出循环
        open_set.remove(current_cell)
        closed_set.add(current_cell)
        # 路网点增强
        if(road_adjacency_list is not None):
            RoadpointStrategy.roadpoint_enhance(current_cell, road_adjacency_list, open_set, end_cell)
        for neighbor in current_cell.neighbors:
            if neighbor in map.cells and map.cells[neighbor] not in closed_set:
                # 拒绝策略
                if RejectStrategy.reject_cell(current_cell, map.cells[neighbor], map):
                    continue
                # 计算g值的增量
                g_increment = h3.point_dist(current_cell.center, map.cells[neighbor].center)
                # 奖励策略
                RewardStrategy.reward_cell_by_road(map.cells[neighbor], g_increment)
                # g值更新
                g = current_cell.g + g_increment
                if map.cells[neighbor] not in open_set or g < map.cells[neighbor].g:
                    map.cells[neighbor].g = g
                    map.cells[neighbor].h = h3.point_dist(map.cells[neighbor].center, end_cell.center)
                    map.cells[neighbor].f = 0.95 * map.cells[neighbor].g + map.cells[neighbor].h
                    map.cells[neighbor].father = current_cell  # 设置父节点
                    open_set.add(map.cells[neighbor])

    # 生成路径
    while current_cell:
        path.add_cell(current_cell)
        current_cell = current_cell.father
    return path

def write_path_shp(path_points, shp_path):
    """
    将路径点写入SHP文件,并生成对应的PRJ文件以定义WGS84坐标系
    :param path_points: 路径点列表 [(lat1, lon1), (lat2, lon2), ...]
    :param shp_path: 输出的SHP文件路径
    :return: None
    """
    import shapefile as shp
    from shapely.geometry import LineString

    # 转换路径点格式为 (lon, lat)
    path_points = [(lon, lat) for lat, lon in path_points]

    # 创建一个新的SHP文件，指定类型为 PolyLine (3)
    with shp.Writer(shp_path, shapeType=shp.POLYLINE) as writer:
        writer.field('id', 'N')

        # 写入路径线
        line = LineString(path_points)
        writer.line([list(line.coords)])
        writer.record(1)  # 确保记录数量与几何形状数量一致

    # 创建对应的PRJ文件，定义WGS84坐标系
    prj_path = shp_path.replace('.shp', '.prj')
    with open(prj_path, 'w') as prj_file:
        prj_file.write("""GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.0174532925199433,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4326"]]""")

if __name__ == "__main__":
    with open('output/汤山/汤山map.bin', 'rb') as f:
        map = pickle.load(f)
    start = (31.989187,118.990892)
    end = (31.996765,118.982489)
    path = pp(map, start, end)
    path_points = []
    for cell in path.cells.values():
        path_points.append(cell.center)
    write_path_shp(path_points, 'output/汤山/规划路径.shp')

