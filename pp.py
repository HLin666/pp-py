import pickle
import h3
import data_structures
from pp_enum import *

def init_attributes_index(map):
    """
    初始化属性索引
    :param map: 地图对象
    :return: attributes_index: 属性索引列表
    """
    # 初始化一个元素为-1的属性索引列表
    attributes_index = 3 * [-1]
    flag = 0
    # 遍历地图的属性列表
    for i, attribute in enumerate(map.attributes):
        if attribute == StringConstant.ELEVATION.value or attribute == StringConstant.SLOPE.value:
            flag += 1
        elif attribute == StringConstant.CV.value:
            attributes_index[AttributeIndex.CV.value]=i-flag
        elif attribute == StringConstant.RELIEF.value:
            attributes_index[AttributeIndex.RELIEF.value]=i-flag
        elif attribute == StringConstant.ROUGHNESS.value:
            attributes_index[AttributeIndex.ROUGHNESS.value]=i-flag
    return attributes_index

def reject_cell_by_cv(neighbor_cell, cv_index, cv_threshold):
    if neighbor_cell.attribute[cv_index].value == None:
        return True
    if cv_index != -1 and neighbor_cell.attribute[cv_index].value > cv_threshold:
        return True
    return False

def reject_cell_by_road(current_cell, neighbor_cell):
    if current_cell.road_topology_type == RoadTopologyType.ISOLATEDWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.NOWAY.value:
        return True
    elif current_cell.road_topology_type == RoadTopologyType.NOWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.ISOLATEDWAY.value:
        return True
    else:
        return False

def reject_cell(current_cell, neighbor_cell, attributes_index):
    """
    判断一个cell是否被拒绝
    :param cell: Cell对象
    :param map_attributes: 地图属性列表
    :param attributes_index: 属性索引列表
    :return: bool
    """
    # 模拟阈值
    cv_threshold = 0.1
    cv_index = attributes_index[AttributeIndex.CV.value]
    if reject_cell_by_cv(neighbor_cell, cv_index, cv_threshold):
        return True
    if reject_cell_by_road(current_cell, neighbor_cell):
        return True
    return False

def has_passable_road(current_cell, neighbor_cell):
    """
    判断一个cell是否有可通行的道路
    :param current_cell: 当前cell
    :param neighbor_cell: 邻接cell
    :return: bool
    """
    if current_cell.road_topology_type == RoadTopologyType.NOWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.CONNECTEDWAY.value:
        return True
    elif current_cell.road_topology_type == RoadTopologyType.ISOLATEDWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.ISOLATEDWAY.value:
        return True
    elif current_cell.road_topology_type == RoadTopologyType.ISOLATEDWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.CONNECTEDWAY.value:
        return True
    elif current_cell.road_topology_type == RoadTopologyType.CONNECTEDWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.ISOLATEDWAY.value:
        return True
    elif current_cell.road_topology_type == RoadTopologyType.CONNECTEDWAY.value and neighbor_cell.road_topology_type == RoadTopologyType.CONNECTEDWAY.value:
        return True
    return False


def pp(map, start, end):
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
    path = data_structures.Map()  # 最终路径
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
    attributes_index = init_attributes_index(map) # 属性索引表
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
        for neighbor in current_cell.neighbors:
            if neighbor in map.cells and map.cells[neighbor] not in closed_set:
                # 执行拒绝策略
                if has_passable_road(current_cell, map.cells[neighbor]):
                    pass # 有可供通行的道路，无需考虑其他的限制，凌驾一切
                elif reject_cell(current_cell, map.cells[neighbor], attributes_index):
                    continue
                # 计算g值
                g = current_cell.g + h3.point_dist(current_cell.center, map.cells[neighbor].center)
                if has_passable_road(current_cell, map.cells[neighbor]):
                    g *= 0.1
                if map.cells[neighbor] not in open_set or g < map.cells[neighbor].g:
                    map.cells[neighbor].g = g
                    map.cells[neighbor].h = h3.point_dist(map.cells[neighbor].center, end_cell.center)
                    map.cells[neighbor].f = map.cells[neighbor].g + map.cells[neighbor].h
                    map.cells[neighbor].father = current_cell  # 设置父节点
                    open_set.add(map.cells[neighbor])

    # 生成路径
    while current_cell:
        path.add_cell(current_cell)
        current_cell = current_cell.father
    return path

if __name__ == "__main__":
    with open('data/玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    # start = (32.052653,118.822807)
    # end = (32.074446,118.814145)
    start = (32.056379,118.804974)
    end = (32.069695,118.801675)
    path = pp(map, start, end)
    # 保存路径
    with open('data/path.bin', 'wb') as f:
        pickle.dump(path, f)
    print("路径规划完成")

