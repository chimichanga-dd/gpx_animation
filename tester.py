import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import gpx_parser
import os
import imageio.v3 as iio
from pygifsicle import optimize
import numpy as np
import imageio.v3 as iio
import math
import time


start_time = time.time()


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

fig, ax = plt.subplots()
crs_projection = "EPSG:4326"
within_1_previous_tracks = {"lats": [], "lons": []}
after_1_previous_tracks = {"lats": [], "lons": []}



def plot_points(axis, lats, lons, color="red"):
    if lats and lons:
        gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(
                lons,
                lats,
            ),
            crs=crs_projection,
        )

        xy = gdf["geometry"].map(lambda point: point.xy)
        x, y = zip(*xy)

        axis.scatter(x=x, y=y, color=color, s=4)
    return axis


# create images
for idx in range(0, combined_gpx_attributes["last_step"], step):
    if (
        idx not in combined_gpx_attributes["lats"]
        or idx not in combined_gpx_attributes["lons"]
    ):
        continue

    ax.cla()

    ax.set_xlim(plot_border_x_min, plot_border_x_max)
    ax.set_ylim(plot_border_y_min, plot_border_y_max)
    ax.axis("off")
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)

    cx.add_basemap(
        ax,
        crs=crs_projection,
        attribution="",
    )

    current_lats = combined_gpx_attributes["lats"][idx]
    current_lons = combined_gpx_attributes["lons"][idx]

    plot_points(
        ax,
        after_1_previous_tracks["lats"],
        after_1_previous_tracks["lons"],
        "#e59866",
    )
    plot_points(
        ax,
        within_1_previous_tracks["lats"],
        within_1_previous_tracks["lons"],
        "#d35400",
    )
    plot_points(
        ax,
        current_lats,
        current_lons,
        "#a04000",
    )


    # save image
    print(
        f"saving plot for step {int(idx / step + 1)} of {int(combined_gpx_attributes['last_step'] / step)}"
    )
    image_file_path = f"{images_folder}/foo{idx}.png"
    plt.savefig(image_file_path, bbox_inches="tight", pad_inches=0)
    file_names.append(image_file_path)

    # prep for next round
    after_1_previous_tracks["lats"].extend(within_1_previous_tracks["lats"])
    after_1_previous_tracks["lons"].extend(within_1_previous_tracks["lons"])
    within_1_previous_tracks["lats"] = current_lats
    within_1_previous_tracks["lons"] = current_lons

plt.close()


gif_path = "./gpx_combined.gif"

frames = np.stack([iio.imread(filename) for filename in file_names], axis=0)
iio.imwrite(gif_path, frames)
optimize(gif_path)

print(time.time() - start_time, "seconds")
