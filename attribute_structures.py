from data_structures import Attribute, SubAttribute

class Elevation(Attribute):
    """高程属性"""
    def __init__(self, value):
        super().__init__(value)

class Slope(Attribute):
    """坡度属性"""
    def __init__(self, value):
        super().__init__(value)

class Exposure(Attribute):
    """坡向属性"""
    def __init__(self, value):
        super().__init__(value)

class Curvature(Attribute):
    """曲率属性"""
    def __init__(self, value):
        super().__init__(value)

class Roughness(Attribute):
    """地形粗糙度属性"""
    def __init__(self, value):
        super().__init__(value)

class Relief(Attribute):
    """地形起伏度属性"""
    def __init__(self, value):
        super().__init__(value)

class ElevationCoefficientOfVariation(Attribute):
    """高程变异系数属性"""
    def __init__(self, value):
        super().__init__(value)

class Water(Attribute):
    """
    水体属性
    """
    class WaterDepth(SubAttribute):
        """水深子属性"""
        def __init__(self, value):
            super().__init__(value)

    class WaterBottomGeology(SubAttribute):
        """水底地质子属性"""
        def __init__(self, value):
            super().__init__(value)

    class FlowSpeed(SubAttribute):
        """流速子属性"""
        def __init__(self, value):
            super().__init__(value)
    class WaterWidth(SubAttribute):
        """水体宽度子属性"""
        def __init__(self, value):
            super().__init__(value)
    class BankSteepness(SubAttribute):
        """岸边陡峭程度子属性"""
        def __init__(self, value):
            super().__init__(value)

    def __init__(self, value):
        super().__init__(value)

class Vegetation(Attribute):
    """
    植被属性
    """
    class VegetationType(SubAttribute):
        """植被类型子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class VegetationDensity(SubAttribute):
        """植被密度子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class AverageVegetationHeight(SubAttribute):
        """平均植被高度子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class AveragePlantDiameter(SubAttribute):
        """平均植株胸径子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class CanopyClosure(SubAttribute):
        """林冠层郁闭度子属性"""
        def __init__(self, value):
            super().__init__(value)

    def __init__(self, value):
        super().__init__(value)

class Soil(Attribute):
    """
    土壤属性
    """
    class SoilType(SubAttribute):
        """土壤类型子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class SoilHardness(SubAttribute):
        """土壤硬度子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class SoilBearingCapacity(SubAttribute):
        """土壤承载力子属性"""
        def __init__(self, value):
            super().__init__(value)

    class SurfaceSoilThickness(SubAttribute):
        """表层土厚度子属性"""
        def __init__(self, value):
            super().__init__(value)

    def __init__(self, value):
        super().__init__(value)

class Building(Attribute):
    """
    建筑物属性
    """
    class BuildingType(SubAttribute):
        """建筑物类型子属性"""
        def __init__(self, value):
            super().__init__(value)

    class BuildingHardness(SubAttribute):
        """建筑物硬度子属性"""
        def __init__(self, value):
            super().__init__(value)
    
    class BuildingDestructibility(SubAttribute):
        """建筑物可破坏性子属性"""
        def __init__(self, value):
            super().__init__(value)

    def __init__(self, value):
        super().__init__(value)

if __name__ == '__main__':
    # 水体属性示例代码
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
    print(f"水体属性: {water.get_value()}")
    print(f"水深: {water.get_sub_attribute(Water.WaterDepth).get_value()}")
    print(f"水底地质: {water.get_sub_attribute(Water.WaterBottomGeology).get_value()}")
    print(f"流速: {water.get_sub_attribute(Water.FlowSpeed).get_value()}")
    print(f"水体宽度: {water.get_sub_attribute(Water.WaterWidth).get_value()}")
    print(f"岸边陡峭程度: {water.get_sub_attribute(Water.BankSteepness).get_value()}")
    # 植被属性示例代码
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
    print(f"植被属性: {vegetation.get_value()}")
    print(f"植被类型: {vegetation.get_sub_attribute(Vegetation.VegetationType).get_value()}")
    print(f"植被密度: {vegetation.get_sub_attribute(Vegetation.VegetationDensity).get_value()}")
    print(f"平均植被高度: {vegetation.get_sub_attribute(Vegetation.AverageVegetationHeight).get_value()}")
    print(f"平均植株胸径: {vegetation.get_sub_attribute(Vegetation.AveragePlantDiameter).get_value()}")
    print(f"林冠层郁闭度: {vegetation.get_sub_attribute(Vegetation.CanopyClosure).get_value()}")
    # 土壤属性示例代码
    soil = Soil("土壤")
    soil_type = Soil.SoilType("粘土")
    soil_hardness = Soil.SoilHardness(1.5)
    soil_bearing_capacity = Soil.SoilBearingCapacity(200.0)
    surface_soil_thickness = Soil.SurfaceSoilThickness(0.5)
    soil.add_sub_attribute(soil_type)
    soil.add_sub_attribute(soil_hardness)
    soil.add_sub_attribute(soil_bearing_capacity)
    soil.add_sub_attribute(surface_soil_thickness)
    print(f"土壤属性: {soil.get_value()}")
    print(f"土壤类型: {soil.get_sub_attribute(Soil.SoilType).get_value()}")
    print(f"土壤硬度: {soil.get_sub_attribute(Soil.SoilHardness).get_value()}")
    print(f"土壤承载力: {soil.get_sub_attribute(Soil.SoilBearingCapacity).get_value()}")
    print(f"表层土厚度: {soil.get_sub_attribute(Soil.SurfaceSoilThickness).get_value()}")
    # 建筑物属性示例代码
    building = Building("建筑物")
    building_type = Building.BuildingType("高层建筑")
    building_hardness = Building.BuildingHardness(2.0)
    building_destructibility = Building.BuildingDestructibility("可破坏")
    building.add_sub_attribute(building_type)
    building.add_sub_attribute(building_hardness)
    building.add_sub_attribute(building_destructibility)
    print(f"建筑物属性: {building.get_value()}")
    print(f"建筑物类型: {building.get_sub_attribute(Building.BuildingType).get_value()}")
    print(f"建筑物硬度: {building.get_sub_attribute(Building.BuildingHardness).get_value()}")
    print(f"建筑物可破坏性: {building.get_sub_attribute(Building.BuildingDestructibility).get_value()}")
    
