import rasterio
from rasterio import features
from rasterio_utils import RasterioUtils
import pickle
from tqdm import tqdm

class QuantityTerrain:
    """
    量化地形
    """

    def quantity_terrain(map, terrain_file_path):
        # 读取DEM数据(wgs84坐标系)
        with rasterio.open(terrain_file_path) as src:
            data = src.read(1)          # 读取第一波段数据
            transform = src.transform   # 获取仿射变换
            nodata_value = src.nodata   # 获取缺省值
            out_shape=src.shape         # 获取数据形状
            bounds = src.bounds         # 获取边界范围
        
        # 遍历 Map 中的 Cell 对象
        for cell in tqdm(map.cells.values(), desc="量化地形: "):
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
                out_shape,
                transform,
                invert=True  # 反转掩膜（True表示多边形内部）
            )
            # 提取掩膜区域的值
            masked_data = data[mask]

            # 暂时先这样量化地形
            for terrain in masked_data:
                if terrain != nodata_value:
                    cell.terrain[int(terrain)] = cell.terrain.get(terrain, 0) + 1
            
        return map

if __name__ == '__main__':
    # 读取地图对象
    with open('玄武区.bin', 'rb') as f:
        map = pickle.load(f)
    
    # 量化地形
    map = QuantityTerrain.quantity_terrain(map, r"/home/cc/mydata/玄武区地形.tif")
    
    # 将 map 对象序列化并写入二进制文件
    with open('玄武区_地形.bin', 'wb') as f:
        pickle.dump(map, f)