import pickle
import h3
from data_structures import *
from pp_enum import *
from quantity_roadnet import *

def reject_cell_by_cv(neighbor_cell, map, cv_threshold):
    if(StringConstant.CV.value not in map.attributes):
        return True # 未量化cv，直接拒绝
    cv_index = map.attributes[StringConstant.CV.value]
    if cv_index != -1 and neighbor_cell.attribute[cv_index].value > cv_threshold:
        return True # cv值超过阈值，拒绝
    return False

def reject_cell_by_road(current_cell, neighbor_cell):
    # 这里不是只判断neighbor的原因是防止从不可通行的路网点下车了
    if neighbor_cell.road_type == RoadType.HIGHWAY.value or current_cell == RoadType.HIGHWAY.value:
        return True
    else:
        return False

def reject_cell(current_cell, neighbor_cell, map):
    """
    判断一个cell是否被拒绝
    :param current_cell: 当前节点
    :param neighbor_cell: 邻居
    :param map: 地图对象
    :return: bool
    """
    # if reject_cell_by_cv(neighbor_cell, map, cv_threshold=0.1):
    #     return True
    if reject_cell_by_road(current_cell, neighbor_cell):
        return True
    return False

def reward_cell(neighbor_cell, g_increment):
    """
    奖励策略
    :param neighbor_cell: Cell对象
    :param g: 当前cell的g值
    :return: None
    """
    if neighbor_cell.road_type == RoadType.NORMALWAY.value:
        g_increment *= 0.4

def roadpoint_enhance(current_cell, road_adjacency_list, open_set, end_cell):
    """
    路网点增强
    :param current_cell: 当前Cell对象
    :param road_map: 路网邻接表
    :param open_set: 待评估的节点集合
    :param end_cell: 终点Cell对象
    :return: None
    """
    # 如果当前cell是路口，则增强其邻接cell的g值
    if current_cell.road_type == RoadType.HIGHWAY.value or current_cell.road_type == RoadType.ENTRYWAY.value: # 是路网点
        # 检查current_cell.h3_index是否在路网邻接表中
        if current_cell.h3_index in road_adjacency_list:
            # 遍历当前cell的邻接cell
            for neighbor_index in road_adjacency_list[current_cell.h3_index]:
                # 创建一个新的Cell对象
                neighbor_cell = Cell(neighbor_index)
                g_increment = h3.point_dist(current_cell.center, neighbor_cell.center)
                g_increment *= 0.2  # 奖励策略
                neighbor_cell.g = current_cell.g + g_increment
                neighbor_cell.h = h3.point_dist(neighbor_cell.center, end_cell.center)
                neighbor_cell.f = neighbor_cell.g + neighbor_cell.h
                neighbor_cell.father = current_cell  # 设置父节点
                neighbor_cell.road_type = RoadType.HIGHWAY.value  # 少量这个会有bug
                open_set.add(neighbor_cell) # TODO：目前还没法剔除open_set中的冗余节点，同一个经纬位置上可能会有路网点和普通点重合。

def pp(map, start, end, road_adjacency_list):
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
        roadpoint_enhance(current_cell, road_adjacency_list, open_set, end_cell)
        for neighbor in current_cell.neighbors:
            if neighbor in map.cells and map.cells[neighbor] not in closed_set:
                # 拒绝策略
                if reject_cell(current_cell, map.cells[neighbor], map):
                    continue
                # 计算g值的增量
                g_increment = h3.point_dist(current_cell.center, map.cells[neighbor].center)
                # 奖励策略
                reward_cell(map.cells[neighbor], g_increment)
                # g值更新
                g = current_cell.g + g_increment
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
    start = (32.056379,118.804974)
    end = (32.069695,118.801675)
    roadnet = None
    road_adjacency_list = generate_road_adjacency_list(roadnet, GlobalConfig().h3_resolution)
    path = pp(map, start, end, road_adjacency_list)
    # 保存路径
    with open('data/path.bin', 'wb') as f:
        pickle.dump(path, f)
    print("路径规划完成")

