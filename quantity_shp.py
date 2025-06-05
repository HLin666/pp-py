import geopandas as gpd
import h3
from data_structures import *
from attribute_structures import *
from tqdm import tqdm
from shapely.geometry import Polygon,MultiPolygon

class QuantityShp:
    def quantity_shp(map, shp_file, resolution):
        """
        量化shp文件中的属性到map中
        :param map: 地图对象
        :param shp_file: 输出的shp文件路径
        """
        # 遍历shp文件中的每个几何对象，获取fclass字段和geometry字段
        gdf = gpd.read_file(shp_file)
        for index, row in tqdm(gdf.iterrows(), total=len(gdf), desc="量化"+shp_file):
            fclass = row['fclass']
            geometry = row['geometry']
            # 转为h3.polyfill_geojson所需要的Polygon GeoJSON
            if geometry is None:
                continue
            if isinstance(geometry, MultiPolygon):
                # 遍历 MultiPolygon 中的每个 Polygon
                coordinates = [list(polygon.exterior.coords) for polygon in geometry.geoms]
            elif isinstance(geometry, Polygon):
                # 如果是单个 Polygon，直接获取 exterior
                coordinates = [list(geometry.exterior.coords)]
            geojson = {
                "type": "Polygon",
                "coordinates": coordinates
            }
            # 生存每个要素所覆盖的h3单元
            h3index = h3.polyfill_geojson(geojson, resolution)
            # 遍历每个h3单元，从map中找到对应的cell，根据fclass填充attribute数组
            for index in h3index:
                if index not in map.cells:
                    continue
                cell = map.cells[index]
                # 根据fclass填充cell的属性
                if fclass == 'water': # 水体
                    cell.attribute.append(Water(1))
                    cell.show_attribute = AttributeIndex.WATER.value
                elif fclass == 'forest': # 森林
                    cell.attribute.append(Forest(1))
                    cell.show_attribute = AttributeIndex.FOREST.value
                elif fclass == 'grass': # 草地
                    cell.attribute.append(Grass(1))
                    cell.show_attribute = AttributeIndex.GRASS.value
                elif fclass == 'building': # 建筑物
                    cell.attribute.append(Building(1))
                    cell.show_attribute = AttributeIndex.BUILDING.value
                elif fclass == 'shrubwood': # 灌木丛
                    cell.attribute.append(ShrubWood(1))
                    cell.show_attribute = AttributeIndex.SHRUBWOOD.value
                elif fclass == 'plowland': # 耕地
                    cell.attribute.append(Plowland(1))
                    cell.show_attribute = AttributeIndex.PLOWLAND.value
                elif fclass == 'wasteland': # 荒地
                    cell.attribute.append(Wasteland(1))
                    cell.show_attribute = AttributeIndex.WASTELAND.value
                elif fclass == 'road': # 道路
                    cell.road_type = RoadType.NORMALWAY.value
                    cell.show_attribute = AttributeIndex.ROAD.value
                else:
                    print(f"未知的fclass: {fclass}")

if __name__ == "__main__":
    # 示例用法
    map = Map()
    QuantityShp.quantity_shp(map, 'data/汤山/面状矢量/water.shp', GlobalConfig().h3_resolution)
