import h3
from data_structures import *
from pp_enum import *
from attribute_structures import *

class RejectStrategy:
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
        return False
        
    def reject_cell_by_water(neighbor_cell):
        for attribute in neighbor_cell.attribute:
            if isinstance(attribute, Water):
                return True
        return False
    
    def reject_cell_by_building(neighbor_cell):
        for attribute in neighbor_cell.attribute:
            if isinstance(attribute, Building):
                return True
        return False
    
    def reject_cell_by_forest(neighbor_cell):
        for attribute in neighbor_cell.attribute:
            if isinstance(attribute, Forest):
                return True
        return False
    
    def reject_cell_by_plowland(neighbor_cell):
        for attribute in neighbor_cell.attribute:
            if isinstance(attribute, Plowland):
                return True
        return False
    
    def reject_cell_by_shrubwood(neighbor_cell):
        for attribute in neighbor_cell.attribute:
            if isinstance(attribute, ShrubWood):
                return True
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
        if RejectStrategy.reject_cell_by_road(current_cell, neighbor_cell):
            return True
        if RejectStrategy.reject_cell_by_water(neighbor_cell):
            return True
        if RejectStrategy.reject_cell_by_building(neighbor_cell):
            return True
        if RejectStrategy.reject_cell_by_forest(neighbor_cell):
            return True
        if RejectStrategy.reject_cell_by_plowland(neighbor_cell):
            return True
        if RejectStrategy.reject_cell_by_shrubwood(neighbor_cell):
            return True 
        return False

class RewardStrategy:
    def reward_cell_by_road(neighbor_cell, g_increment):
        """
        奖励策略
        :param neighbor_cell: Cell对象
        :param g: 当前cell的g值
        :return: None
        """
        if neighbor_cell.road_type == RoadType.NORMALWAY.value:
            g_increment *= 0.1
            
class RoadpointStrategy:
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

