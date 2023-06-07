import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as cx
import gpx_parser
import os
import imageio.v3 as iio
from pygifsicle import optimize
import numpy as np
import imageio.v3 as iio
import math


step = 20
file_names = []
images_folder = "./images"
combined_gpx_attributes = {
    "min_lat": math.inf,
    "max_lat": -math.inf,
    "min_lon": math.inf,
    "max_lon": -math.inf,
    "last_step": 0,
    "points": [],
    "lats": {},
    "lons": {},
}

activities = [
    "/Users/daviddixon/Documents/Code/plotter/6189805369.gpx",
    "/Users/daviddixon/Documents/Code/plotter/8754420234.gpx",
]

for activity in activities:
    gpx_parser.parse(activity, combined_gpx_attributes)

# create image directory
isExist = os.path.exists(images_folder)
if not isExist:
    os.makedirs(images_folder)


previous_tracks = {"lats": [], "lons": []}

# create images
for idx in range(0, combined_gpx_attributes["last_step"], step):
    if (
        idx not in combined_gpx_attributes["lats"]
        or idx not in combined_gpx_attributes["lons"]
    ):
        continue

    # plot previous tracks
    prev_df = pd.DataFrame(
        {
            "Latitude": previous_tracks["lats"],
            "Longitude": previous_tracks["lons"],
        }
    )
    old_gdf = geopandas.GeoDataFrame(
        prev_df,
        geometry=geopandas.points_from_xy(prev_df.Longitude, prev_df.Latitude),
        crs="EPSG:4326",
    )
    old_ax = old_gdf.plot(markersize=2, color="red", aspect=1)

    # plot current tracks
    current_lats = combined_gpx_attributes["lats"][idx]
    current_lons = combined_gpx_attributes["lons"][idx]

    new_df = pd.DataFrame(
        {
            "Latitude": current_lats,
            "Longitude": current_lons,
        }
    )
    gdf = geopandas.GeoDataFrame(
        new_df,
        geometry=geopandas.points_from_xy(new_df.Longitude, new_df.Latitude),
        crs="EPSG:4326",
    )
    ax = gdf.plot(ax=old_ax, markersize=2, color="blue")

    # handle image layout
    margin_percent = 0.05
    plot_border_x_min = combined_gpx_attributes["min_lon"] + (
        (combined_gpx_attributes["max_lon"] - combined_gpx_attributes["min_lon"])
        * margin_percent
        * (-1 if combined_gpx_attributes["min_lon"] < 0 else 1)
    )
    plot_border_x_max = combined_gpx_attributes["max_lon"] - (
        (combined_gpx_attributes["max_lon"] - combined_gpx_attributes["min_lon"])
        * margin_percent
        * (-1 if combined_gpx_attributes["max_lon"] < 0 else 1)
    )

    plot_border_y_min = combined_gpx_attributes["min_lat"] - (
        (combined_gpx_attributes["max_lat"] - combined_gpx_attributes["min_lat"])
        * margin_percent
        * (-1 if combined_gpx_attributes["min_lat"] < 0 else 1)
    )
    plot_border_y_max = combined_gpx_attributes["max_lat"] + (
        (combined_gpx_attributes["max_lat"] - combined_gpx_attributes["min_lat"])
        * margin_percent
        * (-1 if combined_gpx_attributes["max_lat"] < 0 else 1)
    )

    ax.set_xlim(plot_border_x_min, plot_border_x_max)
    ax.set_ylim(plot_border_y_min, plot_border_y_max)
    ax.axis("off")
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)

    # print(retval)
    cx.add_basemap(
        ax,
        crs=gdf.crs.to_string(),
        attribution="",
    )

    # save image
    print(
        f"saving plot for step {int(idx / step + 1)} of {int(combined_gpx_attributes['last_step'] / step)}"
    )
    image_file_path = f"{images_folder}/foo{idx}.png"
    plt.savefig(image_file_path, bbox_inches="tight", pad_inches=0)
    plt.close()

    file_names.append(image_file_path)

    # move current tracks into previous tracks
    previous_tracks["lats"].extend(current_lats)
    previous_tracks["lons"].extend(current_lons)


gif_path = "./gpx_combined.gif"

frames = np.stack([iio.imread(filename) for filename in file_names], axis=0)
iio.imwrite(gif_path, frames)
optimize(gif_path)
