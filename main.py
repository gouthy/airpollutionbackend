from osgeo import gdal, osr
import urllib.request
import os 
import datetime
url = "https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndgd/GT.aq/AR.conus/ds.apm25h01_bc.bin"
file_name = "ds.apm25h01_bc.bin"  # Specify the desired file name
def get_last_modified(url):
    try:
        # Send a HEAD request to the server to retrieve metadata only
        response = urllib.request.urlopen(url)
        # Get the headers from the response
        headers = response.info()._headers
        # Search for the 'last-modified' header in the headers
        last_modified_str = next((value for name, value in headers if name.lower() == 'last-modified'), None)
        if last_modified_str:
            # Convert the last modified date string to a datetime object
            last_modified_date = datetime.datetime.strptime(last_modified_str, "%a, %d %b %Y %H:%M:%S %Z")
            return last_modified_date
        else:
            print("Last-Modified header not found for the URL.")
            return None
    except Exception as e:
        print("Error occurred while retrieving last modified information:", e)
        return None

last_modified_date = get_last_modified(url)

if last_modified_date:
    print("Last modified date:", last_modified_date)

if not  os.path.exists(file_name):
    try:
        urllib.request.urlretrieve(url, file_name)
        print("File downloaded successfully.")
    except Exception as e:
        print("An error occurred while downloading the file:", str(e))


if datetime.datetime.fromtimestamp(os.path.getmtime(file_name)) < last_modified_date :
    try:
        urllib.request.urlretrieve(url, file_name)
        print("File downloaded successfully.")
    except Exception as e:
        print("An error occurred while downloading the file:", str(e))



# Input GRIB2 file path
input_grib2_file = "ds.apm25h01_bc.bin"
directory_name = 'geotifffolder'
if not os.path.exists(directory_name):
    # Create the directory
    os.makedirs(directory_name)

# Output folder path where COGs will be saved
output_folder = directory_name

import os
from osgeo import gdal, osr


# Define input and output file paths
input_file = input_grib2_file

# Open the GRIB2 file using GDAL
ds = gdal.Open(input_file)

# Get the projection information from the GRIB2 file
grib_proj = osr.SpatialReference()
grib_proj.ImportFromWkt(ds.GetProjection())

# Create a new SpatialReference object for the desired WGS84 projection
wgs84_proj = osr.SpatialReference()
wgs84_proj.SetWellKnownGeogCS('WGS84')

# Create a Coordinate Transformation object
coord_transform = osr.CoordinateTransformation(grib_proj, wgs84_proj)

# Get the geotransform information from the GRIB2 file
geotransform = ds.GetGeoTransform()

# Retrieve the number of bands and image dimensions
num_bands = 24
width = ds.RasterXSize
height = ds.RasterYSize
# Loop through each band and generate a separate output GeoTIFF file
for band_num in range(1, num_bands + 1):
    band = ds.GetRasterBand(band_num)

    # Read the data as a 2D array
    data = band.ReadAsArray(0, 0, width, height)
    data[data>5000]=0
    # Create an output file path for the current band
    output_file = os.path.join(output_folder, f"pm25_{str(band_num).zfill(2)}_cog.tif")

    # Create an output dataset for the current band
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_file, width, height, 1, gdal.GDT_Float32, options=['TILED=YES', 'COMPRESS=DEFLATE', 'COPY_SRC_OVERVIEWS=YES'])
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    # Write the data to the output GeoTIFF
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(data)

    # Apply band statistics and color table if present
    out_band.SetStatistics(*band.ComputeStatistics(False))
    color_table = band.GetColorTable()
    if color_table:
        out_band.SetColorTable(color_table)

    # Build overviews for the current band's output GeoTIFF
    out_ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32])
    out_ds.FlushCache()

    # Close the output dataset for the current band
    out_ds = None

# Close the input dataset for the GRIB2 file
ds = None


#new file
filesToBeProjected = os.listdir(output_folder) 
for j in range(len(filesToBeProjected)):
    input_file = os.path.join(output_folder, filesToBeProjected[j])
    output_file = input_file[0:25] + 'projected.tif'
    projected_cog = gdal.Warp('temp.tif', input_file, dstSRS="+proj=longlat +ellps=WGS84")
    compressed_cog = gdal.Translate(input_file, projected_cog, creationOptions=["COMPRESS=LZW", "TILED=YES", 'COPY_SRC_OVERVIEWS=YES'])
    projected_cog = None
    compressed_cog = None











