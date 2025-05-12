import pickle
import rasterio
from rasterio_utils import RasterioUtils
import h3
import data_structures
from tqdm import tqdm

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
        """计算中心坡度"""
        if center_elev is None:
            return None
        slope_sum = 0
        count = 0
        for elev in vertex_elevation:
            if elev is not None:
                slope_sum += abs(center_elev - elev) / h3.edge_length(h3.h3_get_resolution(h), unit='m')
                count += 1
        return slope_sum / count if count > 0 else None

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

        return map

if __name__ == '__main__':
    map = QuantityDem.quantity_dem(r"/home/cc/mydata/玄武区dem.tif", resolution=12)
    print(f"地图大小:", len(map.cells))

    # 将 map 对象序列化并写入二进制文件
    with open('玄武区.bin', 'wb') as f:
        pickle.dump(map, f)  # 使用 pickle.dump 序列化对象