from enum import Enum

class H3ResType(Enum):
    """
    h3不同分辨率
    """
    RES_0 = 0
    RES_1 = 1
    RES_2 = 2
    RES_3 = 3
    RES_4 = 4
    RES_5 = 5
    RES_6 = 6
    RES_7 = 7
    RES_8 = 8
    RES_9 = 9
    RES_10 = 10
    RES_11 = 11
    RES_12 = 12
    RES_13 = 13
    RES_14 = 14
    RES_15 = 15

class H3EdgeLength(Enum):
    """
    h3单元不同分辨率对应的边长(m)
    """
    RES_0 = 1107710.0
    RES_1 = 418680.0
    RES_2 = 158240.0
    RES_3 = 59810.0
    RES_4 = 22610.0
    RES_5 = 8540.0
    RES_6 = 3230.0
    RES_7 = 1220.0
    RES_8 = 461.35
    RES_9 = 174.38
    RES_10 = 65.91
    RES_11 = 24.91
    RES_12 = 9.42
    RES_13 = 3.56
    RES_14 = 1.35
    RES_15 = 0.51

class TerrainType(Enum):
    """
    地形类型枚举类
    """
    FOREST = 1   # 林地
    SHRUB = 2    # 灌木
    GRASS = 3    # 草地
    FARM = 4     # 耕地
    BUILDING = 5 # 建筑
    DESERT = 6   # 荒漠
    SNOW = 7     # 雪、冰
    WATER = 8    # 水体
    WETLAND = 9  # 湿地

class StringConstant(Enum):
    """
    字符串常量枚举类
    """
    ELEVATION = "高程"
    SLOPE = "坡度"
    CV = "高程变异系数"
    RELIEF = "地形起伏度"
    ROUGHNESS = "地形粗糙度"

class AttributeIndex(Enum):
    """
    属性索引枚举类
    """
    CV = 0
    RELIEF = 1
    ROUGHNESS = 2

class RoadTopologyType(Enum):
    """
    道路拓扑类型枚举类
    """
    NOWAY = 0 # 无道路
    ISOLATEDWAY = 1 # 不可穿越的道路
    CONNECTEDWAY = 2 # 可穿越的道路