import pickle
import h3
import data_structures

"""初始化"""
# 导入bin文件，将map加载到内存中
with open('data/玄武区.bin', 'rb') as f:
    map = pickle.load(f)

# 输入起终点的wgs84坐标
# 32.052653,118.822807
# 32.074446,118.814145
start = (32.052653,118.822807)
end = (32.074446,118.814145)

# 从0-15分辨率的索引，在map的字典中找出起始点和终点的索引
start_cell = None
end_cell = None
for i in range(0, 16):
    start_index = h3.geo_to_h3(start[0], start[1], i)
    end_index = h3.geo_to_h3(end[0], end[1], i)
    if start_index in map.cells:
        start_cell = map.cells[start_index]
    if end_index in map.cells:
        end_cell = map.cells[end_index]
    if start_cell and end_cell:
        break
if start_cell is None or end_cell is None:
    raise ValueError("起点或终点不在地图范围内")

"""使用A*算法进行路径规划"""
# 模拟阈值
slope_threshold = 0.1
# 初始化变量
open_set = set()  # 待评估的节点集合
closed_set = set()  # 已评估的节点集合
path = data_structures.Map()  # 最终路径
start_cell.g = 0  # 起点的g值
for neighbor in start_cell.neighbors:
    if neighbor in map.cells:
        map.cells[neighbor].father = start_cell  # 设置父节点
        map.cells[neighbor].g = start_cell.g + h3.point_dist(start_cell.center, map.cells[neighbor].center)
        map.cells[neighbor].h = h3.point_dist(map.cells[neighbor].center, end_cell.center)
        map.cells[neighbor].f = map.cells[neighbor].g + map.cells[neighbor].h
        open_set.add(map.cells[neighbor])
closed_set.add(start_cell)
current_cell = None
# 开始A*算法
while open_set:
    # 找到f值最小的节点
    current_cell = min(open_set, key=lambda cell: cell.f)
    # 刷新显示
    print(f"\r距离终点: {current_cell.h:.6f}", end='', flush=True)
    if current_cell == end_cell:
        break  # 找到终点，退出循环
    open_set.remove(current_cell)
    closed_set.add(current_cell)
    for neighbor in current_cell.neighbors:
        if neighbor in map.cells and map.cells[neighbor] not in closed_set:
            # 检查坡度是否超过阈值
            if map.cells[neighbor].slope > slope_threshold:
                continue
            # 计算g值
            g = current_cell.g + h3.point_dist(current_cell.center, map.cells[neighbor].center)
            if map.cells[neighbor] not in open_set or g < map.cells[neighbor].g:
                map.cells[neighbor].g = g
                map.cells[neighbor].h = h3.point_dist(map.cells[neighbor].center, end_cell.center)
                map.cells[neighbor].f = map.cells[neighbor].g + map.cells[neighbor].h
                map.cells[neighbor].father = current_cell  # 设置父节点
                open_set.add(map.cells[neighbor])

# 生成路径
while current_cell:
    path.add_cell(current_cell)
    current_cell = current_cell.father
with open('data/路径规划结果.bin', 'wb') as f:
    pickle.dump(path, f)




