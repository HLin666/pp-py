import h3
from abc import ABC, abstractmethod
from pp_enum import *

# 全局配置类
class GlobalConfig:
    def __init__(self):
        self.h3_resolution = 11         # 地图对象

class Map:
    def __init__(self):
        self.map_range = []         # 地图范围，多边形坐标数组 [(x1, y1), (x2, y2), ...]
        self.cells = {}             # 存储Cell对象的哈希表，键为h3_index，值为Cell对象
        self.attributes = {}        # 已经量化的属性，存储字符串

    def add_cell(self, cell):
        self.cells[cell.h3_index] = cell

class Cell:
    def __init__(self, h3_index):
        # 格网索引
        self.h3_index = h3_index

        # 几何属性
        self.vertices = []            # 格点坐标数组 [(lat1, lon1), (lat2, lon2), ...]
        self.init_vertices()          # 初始化格点坐标

        self.center = ()              
        self.init_center()            # 初始化格心坐标

        # 拓扑关系
        self.neighbors = []           # 邻接单元数组 (存储索引)
        self.init_neighbor()          # 初始化cell的邻接cell的索引

        # 道路矢量量化拓扑属性
        self.road_type = RoadType.NOWAY.value   # 道路类型

        # dem量化属性
        self.elevation = None         # 高程值
        self.slope = None             # 坡度值
        self.terrain = {}             # 地形类型

        # 其他属性
        self.attribute = []           # 属性数组 (存储Attribute对象)

        # pp相关
        self.g = 0
        self.h = 0
        self.f = 0
        self.father = None

    def init_center(self):
        """
        初始化格心坐标
        """
        # 获取格心坐标
        self.center = h3.h3_to_geo(self.h3_index)

    def init_vertices(self):
        """
        初始化格点坐标
        """
        # 获取格点坐标
        self.vertices = h3.h3_to_geo_boundary(self.h3_index, geo_json=False)

    def init_neighbor(self):
        """
        初始化cell的邻接cell
        """
        neighbor_indexes = h3.k_ring(self.h3_index, 1)  # 获取邻接cell的h3索引
        neighbor_indexes.discard(self.h3_index)  # 移除自身索引
        self.neighbors = [index for index in neighbor_indexes]  # 填充邻接cell的索引
        
# 属性抽象类
class Attribute(ABC):
    def __init__(self, value):
        self.value = value
        self.sub_attribute = []

    def add_sub_attribute(self, sub_attribute):
        """
        添加子属性
        """
        self.sub_attribute.append(sub_attribute)

    def get_value(self):
        """
        获取当前属性值
        """
        return self.value
    
    def get_sub_attribute(self, target_class):
        """
        获取子属性
        """
        for sub in self.sub_attribute:
            if isinstance(sub, target_class):
                return sub
        return None
    
# 子属性抽象类
class SubAttribute(ABC):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        """
        获取当前子属性值
        """
        return self.value
