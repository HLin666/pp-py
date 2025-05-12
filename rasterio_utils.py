import rasterio

class RasterioUtils:
    def lonlat_to_pixel(transform, lon, lat):
        """将经纬度转换为栅格的行列索引"""
        col, row = ~transform * (lon, lat)
        return int(row), int(col)

    def get_value(data, transform, lon, lat, nodata_value):
        """根据经纬度获取高程"""
        row, col = RasterioUtils.lonlat_to_pixel(transform, lon, lat)
        if 0 <= row < data.shape[0] and 0 <= col < data.shape[1]:
            value = float(data[row, col])
            return value if value != nodata_value else None  # 排除缺省值
        return None  # 超出边界返回 None
    
    def is_within_bounds(lat, lon, bounds):
        """判断经纬度是否在栅格范围内"""
        min_lon, min_lat = bounds.left, bounds.bottom
        max_lon, max_lat = bounds.right, bounds.top
        return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat