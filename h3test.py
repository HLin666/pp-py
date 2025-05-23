import pickle
import sys
from pympler import asizeof
from data_structures import Cell
from quantity_dem import QuantityDem
from quantity_terrain import QuantityTerrain
from quantity_cv import QuantityCV
from quantity_relief import QuantityRelief
from quantity_roughness import QuantityRoughness
from quantity_road import QuantityRoad
from quantity_curvature import QuantityCurvature
from quantity_exposure import QuantityExposure
from map2shp import write_cells_to_shp
import os
import h3
from attribute_structures import *


# with open('data/玄武区.bin', 'rb') as f:
#     map = pickle.load(f)


def quantity_test(dem_path,resolution,road_shp_path):
    """量化测试"""
    """
    dem_path = r"/home/cc/mydata/玄武区dem.tif"
    road_shp_path = r"/home/cc/mydata/road_shp/road.shp"
    resolution = 11
    quantity_test(dem_path,resolution,road_shp_path)
    """
    map=QuantityDem.quantity_dem(dem_path,resolution)
    QuantityCurvature.quantity_curvature(map)
    QuantityCV.quantity_cv(map,dem_path)
    QuantityExposure.quantity_exposure(map)
    QuantityRelief.quantity_relief(map,dem_path)
    QuantityRoughness.quantity_roughness(map,dem_path)
    QuantityRoad.quantity_road(map,road_shp_path) # 量化路网
    return map

def fullload_run(map):
    """满载运行"""
    # 水体属性
    water = Water("水体")
    water_depth = Water.WaterDepth(5.0)
    water_bottom_geology = Water.WaterBottomGeology("沙质底")
    flow_speed = Water.FlowSpeed(1.5)
    water_width = Water.WaterWidth(10.0)
    bank_steepness = Water.BankSteepness("陡峭")
    water.add_sub_attribute(water_depth)
    water.add_sub_attribute(water_bottom_geology)
    water.add_sub_attribute(flow_speed)
    water.add_sub_attribute(water_width)
    water.add_sub_attribute(bank_steepness)
    # 植被属性
    vegetation = Vegetation("植被")
    vegetation_type = Vegetation.VegetationType("阔叶林")
    vegetation_density = Vegetation.VegetationDensity(0.8)
    average_vegetation_height = Vegetation.AverageVegetationHeight(15.0)
    average_plant_diameter = Vegetation.AveragePlantDiameter(0.3)
    canopy_closure = Vegetation.CanopyClosure(0.7)
    vegetation.add_sub_attribute(vegetation_type)
    vegetation.add_sub_attribute(vegetation_density)
    vegetation.add_sub_attribute(average_vegetation_height)
    vegetation.add_sub_attribute(average_plant_diameter)
    vegetation.add_sub_attribute(canopy_closure)
    # 土壤属性
    soil = Soil("土壤")
    soil_type = Soil.SoilType("粘土")
    soil_hardness = Soil.SoilHardness(1.5)
    soil_bearing_capacity = Soil.SoilBearingCapacity(200.0)
    surface_soil_thickness = Soil.SurfaceSoilThickness(0.5)
    soil.add_sub_attribute(soil_type)
    soil.add_sub_attribute(soil_hardness)
    soil.add_sub_attribute(soil_bearing_capacity)
    soil.add_sub_attribute(surface_soil_thickness)
    # 建筑物属性
    building = Building("建筑物")
    building_type = Building.BuildingType("高层建筑")
    building_hardness = Building.BuildingHardness(2.0)
    building_destructibility = Building.BuildingDestructibility("可破坏")
    building.add_sub_attribute(building_type)
    building.add_sub_attribute(building_hardness)
    building.add_sub_attribute(building_destructibility)
    for cell in map.cells.values():
        cell.attribute.append(water)
        cell.attribute.append(vegetation)
        cell.attribute.append(soil)
        cell.attribute.append(building)

if __name__ == "__main__":
    dem_path = r"/home/cc/mydata/玄武区dem.tif"
    road_shp_path = r"/home/cc/mydata/road_shp/road.shp"
    resolution = 11
    map = quantity_test(dem_path,resolution,road_shp_path)
    fullload_run(map)
    # 暂停
    input("Press Enter to continue...")

    # with open('data/玄武区.bin', 'wb') as f:
    #     pickle.dump(map, f)
    # # 转为shp
    # output_dir = "data/output_shp"
    # os.makedirs(output_dir, exist_ok=True)
    # shp_path = os.path.join(output_dir, "玄武区.shp")
    # write_cells_to_shp(map, shp_path)