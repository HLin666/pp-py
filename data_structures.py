import h3

class Map:
    def __init__(self):
        self.map_range = []         # 地图范围，多边形坐标数组 [(x1, y1), (x2, y2), ...]
        self.cells = {}             # 存储Cell对象的哈希表，键为h3_index，值为Cell对象

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
        self.neighbors = []           # 邻接单元数组 (存储Cell对象)
        self.init_neighbor()          # 初始化cell的邻接cell的索引

        # 矢量量化属性
        self.highway_edges = []       # 公路通行边数组 (bool列表，索引对应neighbors)
        self.has_highway = False      # 是否包含公路

        # 栅格量化属性
        self.elevation = None         # 高程值
        self.slope = None             # 坡度值
        self.exposure = None          # 坡向值
        self.terrain = {}             # 地形类型

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
        
