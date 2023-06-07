import pandas as pd
import geopandas
import matplotlib.pyplot as plt
from geodatasets import get_path
import contextily as cx
import gpx_parser
import os
import imageio


activity_file_path = "/Users/daviddixon/Documents/Code/plotter/6189805369.gpx"
activity_file_path = "/Users/daviddixon/Documents/Code/plotter/8754420234.gpx"
gpx_data = gpx_parser.parse(activity_file_path)
step = 20
file_names = []
path = "./images"

#create image directory
isExist = os.path.exists(path)
if not isExist:
   os.makedirs(path)

#create images
for idx in range(0, len(gpx_data["points"]), step):
    prev_df = pd.DataFrame(
        {
            "Latitude": gpx_data["lats"][0: idx] if idx > step else [],
            "Longitude": gpx_data["lons"][0: idx] if idx > step else [],
        }
    )
    old_gdf = geopandas.GeoDataFrame(
        prev_df, geometry=geopandas.points_from_xy(prev_df.Longitude, prev_df.Latitude), crs="EPSG:4326",
        
    )
    old_ax = old_gdf.plot(markersize=2, color="red", aspect=1)

    new_df = pd.DataFrame(
        {
            "Latitude": gpx_data["lats"][idx: idx + step],
            "Longitude": gpx_data["lons"][idx: idx + step],
        }
    )
    gdf = geopandas.GeoDataFrame(
        new_df, geometry=geopandas.points_from_xy(new_df.Longitude, new_df.Latitude), crs="EPSG:4326"
    )
    ax = gdf.plot(ax=old_ax,markersize=2, color="blue")

    ax.set_xlim(gpx_data["min_lon"], gpx_data["max_lon"])
    ax.set_ylim(gpx_data["min_lat"], gpx_data["max_lat"])
    ax.axis('off')
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)

    cx.add_basemap(ax, crs=gdf.crs.to_string(), attribution="")
    print(f"saving image {idx / 20} of {len(gpx_data['points']) / 20}")
    image_file_path = f'{path}/foo{idx}.png'
    plt.savefig(image_file_path, bbox_inches='tight', pad_inches=0)
    file_names.append(image_file_path)
    plt.close()

#create gif using images
with imageio.get_writer('./gpx_combined.gif', mode='I') as writer:
    for filename in file_names:
        image = imageio.imread(filename)
        writer.append_data(image)