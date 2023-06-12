import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import gpx_parser_v2
import os
import imageio.v3 as iio
from pygifsicle import optimize
import numpy as np
import imageio.v3 as iio
import math
import time
from memory_profiler import profile
import matplotlib.animation as animation


# instantiating the decorator
def pad_with_zero(number):
    return f"0{number}" if number < 10 else number


def plot_points(axis, lats, lons, color="red", crs_projection="EPSG:4326"):
    if lats and lons:
        points = gpd.points_from_xy(
            lons,
            lats,
        )
        xy = []
        for point in points:
            xy.append(point.xy)
        x, y = zip(*xy)

        axis.scatter(x=x, y=y, color=color, s=4)
    return axis


def updateline(num, routes, file_names):
    for idx, route in enumerate(routes):
        line, points = route
        line.set_data(points[..., : num * 5])
        print(f"saving plot for step {int(num)}:{idx} of {int(len(points[0])//5)}")
    # return line1


def main():
    activities = [
        "/Users/daviddixon/Documents/Code/plotter/6189805369.gpx",
        "/Users/daviddixon/Documents/Code/plotter/8754420234.gpx",
        "/Users/daviddixon/Documents/Code/plotter/Tough_Stuff.gpx",
    ]
    images_folder = "./images"
    gif_path = "./gpx_combined.gif"
    step = 20
    file_names = []
    combined_gpx_attributes = {
        "min_lat": math.inf,
        "max_lat": -math.inf,
        "min_lon": math.inf,
        "max_lon": -math.inf,
        "last_step": 0,
        "points": [],
        "lats": {},
        "lons": {},
        "routes": [],
    }
    crs_projection = "EPSG:4326"
    within_1_previous_tracks = {"lats": [], "lons": []}
    after_1_previous_tracks = {"lats": [], "lons": []}

    for activity in activities:
        gpx_parser_v2.parse(activity, combined_gpx_attributes)

    # create image directory
    isExist = os.path.exists(images_folder)
    if not isExist:
        os.makedirs(images_folder)

    fig = plt.figure(figsize=(16, 9), dpi=(1920 / 16))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

    # plt.margins(0, 0)
    ax = fig.add_subplot()

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

    cx.add_basemap(
        ax, crs=crs_projection, attribution="", source=cx.providers.Esri.WorldGrayCanvas
    )

    lines = []
    max_frames = -math.inf
    for route in combined_gpx_attributes["routes"]:
        (l,) = ax.plot([], [], "o", ls="-", markevery=[-1], mfc="red", mec="blue")

        points_len = len(route)
        pointsLon = []
        pointsLat = []
        for idx in range(points_len):
            point = route[idx]
            pointsLon.append(point["lon"])
            pointsLat.append(point["lat"])

        points = np.array([pointsLon, pointsLat])
        max_frames = max(max_frames, points_len)
        lines.append((l, points))

    # print(points)

    anim = animation.FuncAnimation(
        fig,
        updateline,
        fargs=(lines, file_names),
        # frames=(points_len),
        frames=(max_frames // 5),
    )
    writervideo = animation.FFMpegWriter(fps=30)
    anim.save(
        "tester.mp4",
        writer=writervideo,
    )


start_time = time.time()
main()
print(time.time() - start_time, "seconds")
