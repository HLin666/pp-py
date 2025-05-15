import pickle
import rasterio
from rasterio import features
from rasterio_utils import RasterioUtils
from statistics import stdev, mean
from attribute_structures import ElevationCoefficientOfVariation
from tqdm import tqdm

class QuantityCV:
    """
    量化高程变异系数
    """
    def quantity_cv(map, dem_path, mask=False):
            # 掩膜法
            if mask:
                # 读取DEM数据(wgs84坐标系)
                with rasterio.open(dem_path) as src:
                    data = src.read(1)          # 读取第一波段数据
                    transform = src.transform   # 获取仿射变换
                    nodata_value = src.nodata   # 获取缺省值
                    bounds = src.bounds         # 获取边界范围
                for cell in tqdm(map.cells.values(), desc="量化高程变异系数: "):
                    # 根据cell中心点坐标判断cell是否超出tif文件范围
                    if not RasterioUtils.is_within_bounds(cell.center[0], cell.center[1], bounds):
                        continue
                    # 根据cell的六个顶点坐标构建geojson
                    geojson = {
                        "type": "Polygon",
                        "coordinates": [[
                            (lon, lat) for lat, lon in cell.vertices
                        ]]
                    }
                    # 创建栅格掩膜
                    mask = features.geometry_mask(
                        [geojson],
                        data.shape,
                        transform,
                        invert=True  # 反转掩膜（True表示多边形内部）
                    )
                    # 提取掩膜区域的值
                    masked_data = data[mask]
                    elevations = []
                    # 遍历掩膜区域的值
                    for elev in masked_data:
                        if elev != nodata_value:
                            elevations.append(elev)
                    # 计算标准差
                    if len(elevations) >= 2:
                        avg = mean(elevations)    # 平均值
                        sd = stdev(elevations)     # 标准差
                        cv = ElevationCoefficientOfVariation(round(sd / avg, 4) if avg != 0 else None)
                        cell.attribute.append(cv)
            # 邻域法
            else:
                for cell in tqdm(map.cells.values(), desc="量化高程变异系数: "):
                    elevations = []

                    # 包含自身
                    if cell.elevation is not None:
                        elevations.append(cell.elevation)

                    # 包含6个邻接单元
                    for neighbor_index in cell.neighbors:
                        neighbor_cell = map.cells.get(neighbor_index)
                        if neighbor_cell and neighbor_cell.elevation is not None:
                            elevations.append(neighbor_cell.elevation)


                    if len(elevations) >= 2:
                        avg = mean(elevations)    # 平均值
                        sd = stdev(elevations)     # 标准差
                        cv = ElevationCoefficientOfVariation(round(sd / avg, 4) if avg != 0 else None)
                        cell.attribute.append(cv)
            return map

if __name__ == '__main__':
    # 读取地图对象
    with open('玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    print(f"该map中现有属性:", map.attributes)
    
    # 量化高程变异系数
    map = QuantityCV.quantity_cv(map, r"/home/cc/mydata/玄武区dem.tif", mask=False)
    map.attributes.append("高程变异系数")

    # 将 map 对象序列化并写入二进制文件
    with open('玄武区.bin', 'wb') as f:
        pickle.dump(map, f)
            