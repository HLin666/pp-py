import pickle
import shapefile
import os
from tqdm import tqdm
from attribute_structures import *

def write_prj_file(shp_path):
    """
    为 Shapefile 文件生成 WGS84 坐标系的 .prj 文件
    """
    wgs84_prj = """GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563]],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433]]"""
    prj_path = os.path.splitext(shp_path)[0] + ".prj"
    with open(prj_path, "w") as prj_file:
        prj_file.write(wgs84_prj)

def write_cells_to_shp(map, shp_path):
    """
    将 Map 对象中的 Cell 写入到 Shapefile 文件中
    """
    # 创建 shapefile writer
    with shapefile.Writer(shp_path) as shp:
        # 定义字段
        shp.field("h3_index", "C", size=20)
        shp.field("elevation", "F", decimal=2)
        shp.field("slope", "F", decimal=2)
        shp.field("terrain", "N", decimal=0)

        # 动态定义字段
        defined_fields = set()
        for cell in map.cells.values():
            for attr in cell.attribute:
                if isinstance(attr, ElevationCoefficientOfVariation) and "cv" not in defined_fields:
                    shp.field("cv", "F", decimal=4)
                    defined_fields.add("cv")
                elif isinstance(attr, Roughness) and "roughness" not in defined_fields:
                    shp.field("roughness", "F", decimal=2)
                    defined_fields.add("roughness")
                elif isinstance(attr, Relief) and "relief" not in defined_fields:
                    shp.field("relief", "F", decimal=2)
                    defined_fields.add("relief")

        # 遍历 Map 中的 Cell 对象
        for cell in tqdm(map.cells.values(), desc="将map转为shp"):
            # 写入属性
            record = [
                cell.h3_index,
                cell.elevation,
                cell.slope,
                max(cell.terrain, key=cell.terrain.get) if cell.terrain else None,
            ]
            for attr in cell.attribute:
                if isinstance(attr, ElevationCoefficientOfVariation):
                    record.append(attr.value)
                elif isinstance(attr, Roughness):
                    record.append(attr.value)
                elif isinstance(attr, Relief):
                    record.append(attr.value)

            shp.record(*record)

            # 写入几何形状
            shp.poly([[(lon, lat) for lat, lon in cell.vertices]])

    # 写入 .prj 文件
    write_prj_file(shp_path)

if __name__ == "__main__":
    # 反序列化 map 对象
    with open('玄武区.bin', 'rb') as f:
        map = pickle.load(f)

    print(f"该 map 中现有属性: {', '.join(map.attributes)}")

    output_dir = "output_shp"
    os.makedirs(output_dir, exist_ok=True)
    shp_path = os.path.join(output_dir, "玄武区.shp")

    write_cells_to_shp(map, shp_path)
    print(f"Shapefile 已写入: {shp_path}")