import pickle
import rasterio
from rasterio_utils import RasterioUtils
import h3
import data_structures
from tqdm import tqdm
import math

class QuantityDem:
    """
    量化高程和坡度
    """

    def calculate_center_elevation(vertex_elevation):
        """计算中心高程"""
        count = 0
        sum_elev = 0
        for elev in vertex_elevation:
            if elev is not None:
                count += 1
                sum_elev += elev
        return sum_elev / count if count > 0 else None 

    def calculate_center_slope(h, vertex_elevation, center_elev):
        """
        使用Horn算法计算H3六边形单元的坡度
        
        参数:
        h: str - H3单元索引
        vertex_elevation: List[float] - 六边形顶点的高程值列表
        center_elev: float - 中心点高程值
        
        返回:
        float: 坡度值（度），如果数据不足则返回None
        """
        if center_elev is None or len(vertex_elevation) != 6:
            return None
            
        # 获取H3单元格大小
        cell_size = h3.edge_length(h3.h3_get_resolution(h), unit='m')
        if cell_size == 0:
            return None
            
        # 构建3x3高程矩阵，中心为当前单元格中心点
        elev_matrix = [[None, None, None],
                      [None, center_elev, None],
                      [None, None, None]]
                      
        # H3六边形顶点在3x3矩阵中的位置映射（顺时针排列，从顶部开始）
        # 0: 上, 1: 右上, 2: 右下, 3: 下, 4: 左下, 5: 左上
        vertex_positions = [
            (0, 1),  # 上
            (0, 2),  # 右上
            (2, 2),  # 右下
            (2, 1),  # 下
            (2, 0),  # 左下
            (0, 0)   # 左上
        ]
        
        # 填充顶点高程值
        valid_points = 0
        for i, elev in enumerate(vertex_elevation):
            if elev is not None:
                row, col = vertex_positions[i]
                elev_matrix[row][col] = elev
                valid_points += 1
                
        # 需要至少4个有效点（包括中心点）才能计算坡度
        if valid_points < 3:  # 3个顶点 + 1个中心点
            return None
            
        # 计算x方向和y方向的梯度
        # Horn算法的权重系数
        dz_dx = (
            (elev_matrix[0][2] if elev_matrix[0][2] is not None else center_elev) +
            2 * (elev_matrix[1][2] if elev_matrix[1][2] is not None else center_elev) +
            (elev_matrix[2][2] if elev_matrix[2][2] is not None else center_elev) -
            (elev_matrix[0][0] if elev_matrix[0][0] is not None else center_elev) -
            2 * (elev_matrix[1][0] if elev_matrix[1][0] is not None else center_elev) -
            (elev_matrix[2][0] if elev_matrix[2][0] is not None else center_elev)
        ) / (8.0 * cell_size)
        
        dz_dy = (
            (elev_matrix[2][0] if elev_matrix[2][0] is not None else center_elev) +
            2 * (elev_matrix[2][1] if elev_matrix[2][1] is not None else center_elev) +
            (elev_matrix[2][2] if elev_matrix[2][2] is not None else center_elev) -
            (elev_matrix[0][0] if elev_matrix[0][0] is not None else center_elev) -
            2 * (elev_matrix[0][1] if elev_matrix[0][1] is not None else center_elev) -
            (elev_matrix[0][2] if elev_matrix[0][2] is not None else center_elev)
        ) / (8.0 * cell_size)
        
        # 计算坡度（度）
        slope_rad = math.atan(math.sqrt(dz_dx * dz_dx + dz_dy * dz_dy))
        slope_deg = math.degrees(slope_rad)
        
        return slope_deg

    def quantity_dem(dem_path, resolution):
        # 读取DEM数据(wgs84坐标系)
        with rasterio.open(dem_path) as src:
            data = src.read(1)          # 读取第一波段数据
            transform = src.transform   # 获取仿射变换
            bounds = src.bounds         # 获取边界范围
            nodata_value = src.nodata   # 获取缺省值

        # 获取 DEM 范围的经纬度边界
        min_lat, max_lat = bounds.bottom, bounds.top
        min_lon, max_lon = bounds.left, bounds.right

        # 获取覆盖区域的 H3 六边形格网
        all_h3_indices = h3.polyfill_geojson({
            "type": "Polygon",
            "coordinates": [[
                [min_lon, min_lat],
                [min_lon, max_lat],
                [max_lon, max_lat],
                [max_lon, min_lat],
                [min_lon, min_lat]
            ]]
        }, resolution)

        # 创建 Map 对象
        map = data_structures.Map()

        for h in tqdm(all_h3_indices, desc="量化高程与坡度: "):
            cell = data_structures.Cell(h)                # 初始化 Cell 对象
            vertex_elevation = []                         # 顶点高程数组
            for lat, lon in cell.vertices:                # 填充顶点高程数组
                elev = RasterioUtils.get_value(data, transform, lon, lat, nodata_value)
                vertex_elevation.append(elev)

            center_elev = QuantityDem.calculate_center_elevation(vertex_elevation)
            center_slope = QuantityDem.calculate_center_slope(h, vertex_elevation, center_elev)

            # 填充 cell对象并添加到Map

            cell.elevation = center_elev
            cell.slope = center_slope
            map.add_cell(cell)

        # 记录属性
        map.attributes.append("高程")
        map.attributes.append("坡度")

        return map

if __name__ == '__main__':
    map = QuantityDem.quantity_dem(r"C:\Users\wyj517\Desktop\pp-py5.23\玄武区.tif", resolution=11)

    # 将 map 对象序列化并写入二进制文件
    with open('data/玄武区.bin', 'wb') as f:
        pickle.dump(map, f)  # 使用 pickle.dump 序列化对象