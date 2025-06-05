import pickle
import rasterio
from rasterio import features
from rasterio_utils import RasterioUtils
from attribute_structures import Relief
from tqdm import tqdm
from pp_enum import *

class QuantityRelief:
    """
    量化地形起伏度
    """
    def quantity_relief(map, dem_path, mask=False):
            # 掩膜法
            if mask:
                # 读取DEM数据(wgs84坐标系)
                with rasterio.open(dem_path) as src:
                    data = src.read(1)          # 读取第一波段数据
                    transform = src.transform   # 获取仿射变换
                    nodata_value = src.nodata   # 获取缺省值
                    bounds = src.bounds         # 获取边界范围
                for cell in tqdm(map.cells.values(), desc="量化地形起伏度: "):
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
                    # 计算地形起伏度
                    if len(elevations) >= 2:
                        relief = Relief(max(elevations) - min(elevations))
                        cell.attribute.append(relief)
                    else:
                        relief = Relief(0)
                        cell.attribute.append(relief)
            # 邻域法
            else:
                for cell in tqdm(map.cells.values(), desc="量化地形起伏度: "):
                    elevations = []

                    # 包含自身
                    if cell.elevation is not None:
                        elevations.append(cell.elevation)

                    # 包含6个邻接单元
                    for neighbor_index in cell.neighbors:
                        neighbor_cell = map.cells.get(neighbor_index)
                        if neighbor_cell and neighbor_cell.elevation is not None:
                            elevations.append(neighbor_cell.elevation)

                    # 计算地形起伏度
                    if len(elevations) >= 2:
                        relief = Relief(max(elevations) - min(elevations))
                        cell.attribute.append(relief)
                    else:
                        relief = Relief(0)
                        cell.attribute.append(relief)
            
            # 记录属性
            if StringConstant.RELIEF.value not in map.attributes:
                map.attributes[StringConstant.RELIEF.value] = len(map.attributes)
            else:
                # TODO
                print(f"警告: {StringConstant.RELIEF.value} 已经存在于地图属性中")

            return map

if __name__ == '__main__':
    # 读取地图对象
    with open('data/玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    print(f"该map中现有属性:", map.attributes)
    
    # 量化地形粗糙度
    map = QuantityRelief.quantity_relief(map, r"/home/cc/mydata/玄武区dem.tif", mask=False)

    # 将 map 对象序列化并写入二进制文件
    with open('data/玄武区.bin', 'wb') as f:
        pickle.dump(map, f)
            