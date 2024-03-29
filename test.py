from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    # exif_data = img._getexif()
    print("exif_data ==================>",exif_data)
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                gps_info = {}
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = value[gps_tag]
                return gps_info
    return None

def get_lat_lon(gps_info):
    lat = gps_info.get('GPSLatitude')
    lon = gps_info.get('GPSLongitude')
    lat_ref = gps_info.get('GPSLatitudeRef', 'N')
    lon_ref = gps_info.get('GPSLongitudeRef', 'E')

    if lat and lon and lat_ref and lon_ref:
        lat_deg = lat[0][0] / lat[0][1]
        lat_min = lat[1][0] / lat[1][1]
        lat_sec = lat[2][0] / lat[2][1]
        lon_deg = lon[0][0] / lon[0][1]
        lon_min = lon[1][0] / lon[1][1]
        lon_sec = lon[2][0] / lon[2][1]

        latitude = lat_deg + (lat_min / 60.0) + (lat_sec / 3600.0)
        longitude = lon_deg + (lon_min / 60.0) + (lon_sec / 3600.0)

        if lat_ref == 'S':
            latitude *= -1
        if lon_ref == 'W':
            longitude *= -1

        return latitude, longitude

    return None

# Example usage:
if __name__ == "__main__":
    image_path = "Electricity bill.jpg"
    gps_info = get_exif_data(image_path)
    if gps_info:
        location = get_lat_lon(gps_info)
        if location:
            print("Location (Latitude, Longitude):", location)
        else:
            print("Location information not found in the image metadata.")
    else:
        print("No EXIF data found in the image.")
