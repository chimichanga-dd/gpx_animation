import pandas as pd
import geopandas
import matplotlib.pyplot as plt
from geodatasets import get_path
import contextily as cx
import gpx_parser


# a = [1,2,3,4]
# step = 2
# for idx in range(0,len(a),step):
#     print(a[idx: idx+step])


activity_file_path = "/Users/daviddixon/Documents/Code/plotter/6189805369.gpx"
activity_file_path = "/Users/daviddixon/Documents/Code/plotter/8754420234.gpx"
gpx_data = gpx_parser.parse(activity_file_path)
# print(gpx_data)

# for idx in range(len(gpx_data["points"])):
df = pd.DataFrame(
    {
        # "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
        # "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
        "Latitude": gpx_data["lats"],
        "Longitude": gpx_data["lons"],
    }
)

gdf = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
)

# print(gdf.head())

# # We can now plot our ``GeoDataFrame``.
# # gdf.plot(ax=ax, color="red")
ax = gdf.plot(color="red")
cx.add_basemap(ax, crs=gdf.crs.to_string())
# plt.text(lon, lat ,'MY SUPER TITLE')
# plt.show()
plt.savefig('foo.png')