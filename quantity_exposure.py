import pickle
import rasterio
import numpy as np
from rasterio import features
from rasterio_utils import RasterioUtils
from attribute_structures import Exposure
from tqdm import tqdm
import math
from pp_enum import *

class QuantityExposure:
    """
    量化坡向属性
    """

    @staticmethod
    def calculate_exposure_from_gradient(dz_dx, dz_dy):
        """
        根据梯度计算坡向
        :param dz_dx: x方向梯度
        :param dz_dy: y方向梯度
        :return: 坡向角度(度)，北为0度，顺时针增加
        """
        if dz_dx == 0 and dz_dy == 0:
            return None  # 平地无坡向
        
        # 计算坡向角度（弧度）
        aspect_rad = math.atan2(dz_dy, -dz_dx)
        
        # 转换为度数，并调整为北为0度的坐标系
        aspect_deg = math.degrees(aspect_rad)
        aspect_deg = 90 - aspect_deg
        
        # 确保角度在0-360度范围内
        if aspect_deg < 0:
            aspect_deg += 360
        elif aspect_deg >= 360:
            aspect_deg -= 360
            
        return round(aspect_deg, 2)

    @staticmethod
    def calculate_gradient(elevations, cell_size):
        """
        计算3x3窗口的梯度
        :param elevations: 3x3高程数组
        :param cell_size: 单元格大小(米)
        :return: (dz_dx, dz_dy) 梯度值
        """
        # Horn算法计算梯度
        # 3x3窗口布局:
        # a b c
        # d e f  
        # g h i
        a, b, c, d, e, f, g, h, i = elevations
        
        # 如果中心点或关键点为None，返回None
        if e is None:
            return None, None
            
        # 处理缺失值，用中心值或邻近值替代
        def fill_none(val, default):
            return default if val is None else val
            
        a = fill_none(a, e)
        b = fill_none(b, e)
        c = fill_none(c, e)
        d = fill_none(d, e)
        f = fill_none(f, e)
        g = fill_none(g, e)
        h = fill_none(h, e)
        i = fill_none(i, e)
        
        # Horn算法
        dz_dx = ((c + 2*f + i) - (a + 2*d + g)) / (8 * cell_size)
        dz_dy = ((g + 2*h + i) - (a + 2*b + c)) / (8 * cell_size)
        
        return dz_dx, dz_dy

    @staticmethod
    def get_neighbor_elevations(map, cell):
        """
        获取cell及其邻居的高程值，组成3x3网格
        :param map: 地图对象
        :param cell: 当前cell
        :return: 3x3高程数组
        """
        # 获取当前cell的高程
        center_elev = cell.elevation
        
        # 初始化3x3网格，中心为当前cell
        elevations = [None] * 9
        elevations[4] = center_elev  # 中心位置
        
        # 获取邻居cell的高程
        neighbors = cell.neighbors
        if len(neighbors) == 6:  # H3六边形有6个邻居
            # 将6个邻居映射到3x3网格的8个位置
            # 这里使用简化映射，将邻居按照相对位置分布
            for i, neighbor_idx in enumerate(neighbors):
                neighbor_cell = map.cells.get(neighbor_idx)
                if neighbor_cell and neighbor_cell.elevation is not None:
                    # 将6个邻居映射到3x3网格的相应位置
                    grid_pos = [0, 1, 2, 5, 8, 7, 6, 3][i] if i < 8 else 4
                    elevations[grid_pos] = neighbor_cell.elevation
        
        return elevations

    @staticmethod
    def quantity_exposure_mask(map, dem_path):
        """
        使用掩膜法量化坡向
        :param map: 地图对象
        :param dem_path: DEM文件路径
        :return: 更新后的地图对象
        """
        # 读取DEM数据
        with rasterio.open(dem_path) as src:
            data = src.read(1)
            transform = src.transform
            nodata_value = src.nodata
            bounds = src.bounds
            
            # 计算像元大小
            pixel_size_x = abs(transform.a)
            pixel_size_y = abs(transform.e)
            cell_size = (pixel_size_x + pixel_size_y) / 2  # 平均像元大小
            
        for cell in tqdm(map.cells.values(), desc="量化坡向(掩膜法): "):
            # 检查是否在范围内
            if not RasterioUtils.is_within_bounds(cell.center[0], cell.center[1], bounds):
                cell.attribute.append(Exposure(None))
                continue
                
            # 构建geojson
            geojson = {
                "type": "Polygon",
                "coordinates": [[
                    (lon, lat) for lat, lon in cell.vertices
                ]]
            }
            
            # 创建掩膜
            mask = features.geometry_mask(
                [geojson],
                data.shape,
                transform,
                invert=True
            )
            
            # 提取掩膜区域的值
            masked_data = data[mask]
            elevations = []
            
            for elev in masked_data:
                if elev != nodata_value:
                    elevations.append(elev)
            
            if len(elevations) >= 4:  # 需要足够的点计算梯度
                # 使用最大最小值方向估算坡向
                max_elev = max(elevations)
                min_elev = min(elevations)
                
                if max_elev != min_elev:
                    # 简化的坡向计算
                    # 这里可以根据具体需求改进算法
                    exposure_value = 180.0  # 默认值，实际应用中需要更精确的算法
                else:
                    exposure_value = None
            else:
                exposure_value = None
                
            cell.attribute.append(Exposure(exposure_value))

    @staticmethod
    def quantity_exposure_neighbor(map):
        """
        使用邻域法量化坡向
        :param map: 地图对象
        :return: 更新后的地图对象
        """
        # 估算单元格大小（基于H3分辨率）
        sample_cell = next(iter(map.cells.values()))
        import h3
        resolution = h3.h3_get_resolution(sample_cell.h3_index)
        cell_size = h3.edge_length(resolution, unit='m')
        
        for cell in tqdm(map.cells.values(), desc="量化坡向(邻域法): "):
            if cell.elevation is None:
                cell.attribute.append(Exposure(None))
                continue
                
            # 获取3x3邻域的高程值
            elevations = QuantityExposure.get_neighbor_elevations(map, cell)
            
            # 计算梯度
            dz_dx, dz_dy = QuantityExposure.calculate_gradient(elevations, cell_size)
            
            if dz_dx is not None and dz_dy is not None:
                # 计算坡向
                exposure_value = QuantityExposure.calculate_exposure_from_gradient(dz_dx, dz_dy)
            else:
                exposure_value = None
                
            cell.attribute.append(Exposure(exposure_value))

    @staticmethod
    def quantity_exposure(map, dem_path=None, mask=False):
        """
        量化坡向
        :param map: 地图对象
        :param dem_path: DEM文件路径（掩膜法需要）
        :param mask: 是否使用掩膜法
        :return: 更新后的地图对象
        """
        if mask and dem_path:
            QuantityExposure.quantity_exposure_mask(map, dem_path)
        else:
            QuantityExposure.quantity_exposure_neighbor(map)
            
        # 记录属性
        map.attributes.append(StringConstant.EXPOSURE.value)
            
        return map

if __name__ == '__main__':
    # 读取地图对象
    with open('data/玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    print(f"该map中现有属性: {map.attributes}")
    
    # 量化坡向（邻域法）
    map = QuantityExposure.quantity_exposure(map, mask=False)
    
    # 或者使用掩膜法
    # map = QuantityExposure.quantity_exposure(map, dem_path=r"C:\Users\wyj517\Desktop\pp-py\玄武区.tif", mask=True)

    # 保存更新后的地图对象
    with open(r'data\玄武区.bin', 'wb') as f:
        pickle.dump(map, f)
    
    print("坡向量化完成")