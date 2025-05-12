import pickle
import sys
from pympler import asizeof
from data_structures import Cell
from quantity_dem import QuantityDem
from quantity_terrain import QuantityTerrain

# # 计算一个cell的字节
# cell = Cell(h3_index="8928308280fffff")
# print(f"h3_index: {asizeof.asizeof(cell.h3_index)} 字节")
# print(f"vertices: {asizeof.asizeof(cell.vertices)} 字节")
# print(f"center: {asizeof.asizeof(cell.center)} 字节")
# print(f"neighbors: {asizeof.asizeof(cell.neighbors)} 字节")
# print(f"highway_edges: {asizeof.asizeof(cell.highway_edges)} 字节")
# print(f"has_highway: {asizeof.asizeof(cell.has_highway)} 字节")
# print(f"elevation: {asizeof.asizeof(cell.elevation)} 字节")
# print(f"Cell 对象总大小: {asizeof.asizeof(cell)} 字节")

# 检查map中cell生成的对不对
with open('玄武区_地形.bin', 'rb') as f:
    map = pickle.load(f)

for i, cell in enumerate(map.cells.values()):
    if i < 10:
        print(cell.terrain,end=" ")
    else:
        break


