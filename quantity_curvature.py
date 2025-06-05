import pickle
import rasterio
import numpy as np
from rasterio import features
from rasterio_utils import RasterioUtils
from attribute_structures import Curvature
from tqdm import tqdm
from pp_enum import *

class QuantityCurvature:
    """
    量化曲率属性
    """
    @staticmethod
    def calculate_curvature(elevations, cell_size):
        """
        计算曲率(使用Horn算法的二阶导数)
        :param elevations: 3x3高程数组
        :param cell_size: 单元格大小(米)
        :return: 曲率值
        """
        # 3x3窗口布局:
        # a b c
        # d e f  
        # g h i
        a, b, c, d, e, f, g, h, i = elevations
        
        # 如果中心点为None，返回None
        if e is None:
            return None
            
        # 处理缺失值，用中心值替代
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
        
        # 计算一阶偏导数
        dz_dx = ((c + 2*f + i) - (a + 2*d + g)) / (8 * cell_size)
        dz_dy = ((g + 2*h + i) - (a + 2*b + c)) / (8 * cell_size)
        
        # 计算二阶偏导数
        d2z_dx2 = ((a + 2*b + c) + (g + 2*h + i) - 2*(d + 2*e + f)) / (3 * cell_size * cell_size)
        d2z_dy2 = ((a + 2*d + g) + (c + 2*f + i) - 2*(b + 2*e + h)) / (3 * cell_size * cell_size)
        d2z_dxdy = ((a + i) - (c + g)) / (4 * cell_size * cell_size)
        
        # 计算平均曲率 (Mean Curvature)
        p = dz_dx
        q = dz_dy
        r = d2z_dx2
        s = d2z_dxdy
        t = d2z_dy2
        
        # 避免除零错误
        denominator = (1 + p*p + q*q)
        if denominator == 0:
            return 0
            
        # 平均曲率公式
        mean_curvature = -((1 + q*q) * r - 2*p*q*s + (1 + p*p) * t) / (2 * (denominator ** 1.5))
        
        return round(mean_curvature * 1000, 6)  # 放大1000倍便于观察，保留6位小数

    @staticmethod
    def calculate_gaussian_curvature(elevations, cell_size):
        """
        计算高斯曲率
        :param elevations: 3x3高程数组
        :param cell_size: 单元格大小(米)
        :return: 高斯曲率值
        """
        # 3x3窗口布局同上
        a, b, c, d, e, f, g, h, i = elevations
        
        if e is None:
            return None
            
        # 处理缺失值
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
        
        # 计算一阶偏导数
        dz_dx = ((c + 2*f + i) - (a + 2*d + g)) / (8 * cell_size)
        dz_dy = ((g + 2*h + i) - (a + 2*b + c)) / (8 * cell_size)
        
        # 计算二阶偏导数
        d2z_dx2 = ((a + 2*b + c) + (g + 2*h + i) - 2*(d + 2*e + f)) / (3 * cell_size * cell_size)
        d2z_dy2 = ((a + 2*d + g) + (c + 2*f + i) - 2*(b + 2*e + h)) / (3 * cell_size * cell_size)
        d2z_dxdy = ((a + i) - (c + g)) / (4 * cell_size * cell_size)
        
        # 高斯曲率公式
        p = dz_dx
        q = dz_dy
        r = d2z_dx2
        s = d2z_dxdy
        t = d2z_dy2
        
        denominator = (1 + p*p + q*q) ** 2
        if denominator == 0:
            return 0
            
        gaussian_curvature = (r * t - s * s) / denominator
        
        return round(gaussian_curvature * 1000000, 6)  # 放大100万倍便于观察

    @staticmethod
    def get_neighbor_elevations(map, cell):
        """
        获取cell及其邻居的高程值,组成3x3网格
        :param map: 地图对象
        :param cell: 当前cell
        :return: 3x3高程数组
        """
        # 获取当前cell的高程
        center_elev = cell.elevation
        
        # 初始化3x3网格，中心为当前cell
        elevations = [None] * 9
        elevations[4] = center_elev  # 中心位置(e)
        
        # 获取邻居cell的高程
        neighbors = cell.neighbors
        if len(neighbors) >= 6:  # H3六边形有6个邻居
            # 将6个邻居映射到3x3网格的8个位置
            # H3邻居索引到3x3网格的映射
            neighbor_mapping = [0, 1, 2, 5, 8, 7, 6, 3]  # 顺时针映射
            
            for i, neighbor_idx in enumerate(neighbors[:6]):
                neighbor_cell = map.cells.get(neighbor_idx)
                if neighbor_cell and neighbor_cell.elevation is not None:
                    grid_pos = neighbor_mapping[i]
                    elevations[grid_pos] = neighbor_cell.elevation
        
        return elevations

    @staticmethod
    def quantity_curvature_mask(map, dem_path, curvature_type='mean'):
        """
        使用掩膜法量化曲率
        :param map: 地图对象
        :param dem_path: DEM文件路径
        :param curvature_type: 曲率类型 ('mean' 或 'gaussian')
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
            cell_size = (pixel_size_x + pixel_size_y) / 2
            
        for cell in tqdm(map.cells.values(), desc=f"量化曲率-{curvature_type}(掩膜法): "):
            # 检查是否在范围内
            if not RasterioUtils.is_within_bounds(cell.center[0], cell.center[1], bounds):
                cell.attribute.append(Curvature(None))
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
            
            if len(elevations) >= 9:  # 需要足够的点计算曲率
                # 将提取的高程数据重新排列成3x3网格（简化处理）
                elevations_grid = elevations[:9] + [None] * (9 - len(elevations[:9]))
                
                if curvature_type == 'gaussian':
                    curvature_value = QuantityCurvature.calculate_gaussian_curvature(elevations_grid, cell_size)
                else:
                    curvature_value = QuantityCurvature.calculate_curvature(elevations_grid, cell_size)
            else:
                curvature_value = None
                
            cell.attribute.append(Curvature(curvature_value))

    @staticmethod
    def quantity_curvature_neighbor(map, curvature_type='mean'):
        """
        使用邻域法量化曲率
        :param map: 地图对象
        :param curvature_type: 曲率类型 ('mean' 或 'gaussian')
        :return: 更新后的地图对象
        """
        # 估算单元格大小（基于H3分辨率）
        sample_cell = next(iter(map.cells.values()))
        import h3
        resolution = h3.h3_get_resolution(sample_cell.h3_index)
        cell_size = h3.edge_length(resolution, unit='m')
        
        for cell in tqdm(map.cells.values(), desc=f"量化曲率-{curvature_type}(邻域法): "):
            if cell.elevation is None:
                cell.attribute.append(Curvature(None))
                continue
                
            # 获取3x3邻域的高程值
            elevations = QuantityCurvature.get_neighbor_elevations(map, cell)
            
            # 计算曲率
            if curvature_type == 'gaussian':
                curvature_value = QuantityCurvature.calculate_gaussian_curvature(elevations, cell_size)
            else:
                curvature_value = QuantityCurvature.calculate_curvature(elevations, cell_size)
                
            cell.attribute.append(Curvature(curvature_value))

    @staticmethod
    def quantity_curvature(map, dem_path=None, mask=False, curvature_type='mean'):
        """
        量化曲率
        :param map: 地图对象
        :param dem_path: DEM文件路径(掩膜法需要)
        :param mask: 是否使用掩膜法
        :param curvature_type: 曲率类型 ('mean' 或 'gaussian')
        :return: 更新后的地图对象
        """
        if mask and dem_path:
            QuantityCurvature.quantity_curvature_mask(map, dem_path, curvature_type)
        else:
            QuantityCurvature.quantity_curvature_neighbor(map, curvature_type)
            
        # 记录属性
        if StringConstant.CURVATURE.value not in map.attributes:
            map.attributes[StringConstant.CURVATURE.value] = len(map.attributes)
        else:
            # TODO
            print(f"警告: {StringConstant.CURVATURE.value} 已经存在于地图属性中")
            
        return map

if __name__ == '__main__':
    # 读取地图对象
    with open('data/玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    print(f"该map中现有属性: {map.attributes}")
    
    # 量化平均曲率（邻域法）
    map = QuantityCurvature.quantity_curvature(map, mask=False, curvature_type='mean')
    
    # 或者量化高斯曲率
    # map = QuantityCurvature.quantity_curvature(map, mask=False, curvature_type='gaussian')
    
    # 或者使用掩膜法
    # map = QuantityCurvature.quantity_curvature(map, dem_path=r"/home/cc/mydata/玄武区dem.tif", mask=True, curvature_type='mean')

    # 保存更新后的地图对象
    with open('data/玄武区.bin', 'wb') as f:
        pickle.dump(map, f)
    
    print("曲率量化完成")