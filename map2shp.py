import pickle
import shapefile
import os
from tqdm import tqdm

def write_prj_file(shp_path):
    """
    为 Shapefile 文件生成 WGS84 坐标系的 .prj 文件
    :param shp_path: Shapefile 文件路径（不含扩展名）
    """
    wgs84_prj = """GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563]],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433]]"""
    prj_path = shp_path.replace(".shp", ".prj")
    with open(prj_path, "w") as prj_file:
        prj_file.write(wgs84_prj)

def write_cells_to_shp(map, shp_path):
    """
    将 Map 对象中的 Cell 写入到 Shapefile 文件中
    :param map: Map 对象
    :param shp_path: 输出的 Shapefile 文件路径
    """
    # 创建 shapefile writer
    with shapefile.Writer(shp_path) as shp:
        # 定义字段
        shp.field("h3_index", "C", size=20)  # h3_index 字段，字符串类型
        shp.field("elevation", "F", decimal=2)  # elevation 字段，浮点数类型
        shp.field("slope", "F", decimal=2) # slope 字段，浮点数类型
        shp.field("terrain", "N", decimal=0)  # terrain 字段，整数类型

        # 遍历 Map 中的 Cell 对象
        for cell in tqdm(map.cells.values(), desc="Processing cells"):
            # 写入属性
            shp.record(
                cell.h3_index,
                cell.elevation,
                cell.slope,
                max(cell.terrain, key=cell.terrain.get) if cell.terrain else None,
            )

            # 写入几何形状
            shp.poly([[(lon, lat) for lat, lon in cell.vertices]])


    # 写入 .prj 文件，指定坐标系为 WGS84
    write_prj_file(shp_path)

if __name__ == "__main__":
    # 反序列化 map 对象
    with open('玄武区_地形.bin', 'rb') as f:
        map = pickle.load(f)
        print(f"恢复的地图大小: {len(map.cells)}")

    output_dir = "output_shp"
    os.makedirs(output_dir, exist_ok=True)
    shp_path = os.path.join(output_dir, "玄武区_地形.shp")

    write_cells_to_shp(map, shp_path)
    print(f"Shapefile 已写入: {shp_path}")