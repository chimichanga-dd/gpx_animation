import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import contextily as cx
import gpx_parser
import os
import numpy as np
import math

import glob


# instantiating the decorator
def pad_with_zero(number):
    return f"0{number}" if number < 10 else number


def updateline(num, fr_number, routes, max_frames, bucket):
    step = bucket
    time_bucket = num * step
    for idx, route in enumerate(routes):
        line, points, time_segment_indexes, last_step, has_marker = [
            route[k]
            for k in (
                "line",
                "points",
                "time_segment_indexes",
                "last_step",
                "has_marker",
            )
        ]

        if (time_bucket >= last_step + step) and has_marker:
            print(f"clearing marker for line-{idx}")
            line.set_marker("")
            route["has_marker"] = False
            continue

        if time_bucket not in time_segment_indexes:
            continue

        print(f"plotting for line-{idx}: step {num} of {max_frames} frames")

        line.set_data(points[..., : time_segment_indexes[time_bucket]])
    idx_in_hours = pad_with_zero((time_bucket // (60 * 60)) % 24)
    idx_in_minutes = pad_with_zero((time_bucket // (60)) % 60)
    idx_in_seconds = pad_with_zero(time_bucket % 60)
    fr_number.set_text(f"{idx_in_hours}:{idx_in_minutes}:{idx_in_seconds}")


def create_animation():
    activities = glob.glob("./only_runs/*.gpx")

    images_folder = "./images"
    combined_gpx_attributes = {
        "min_lat": math.inf,
        "max_lat": -math.inf,
        "min_lon": math.inf,
        "max_lon": -math.inf,
        "last_step": 0,
        "routes": [],
    }
    crs_projection = "EPSG:4326"

    for activity in activities:
        gpx_parser.parse(activity, combined_gpx_attributes)

    # create image directory
    isExist = os.path.exists(images_folder)
    if not isExist:
        os.makedirs(images_folder)

    fig = plt.figure(figsize=(16, 9), dpi=(1920 / 16))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
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

    fr_number = ax.annotate(
        "",
        (1, 1),
        xycoords="axes fraction",
        xytext=(-10, -5),
        textcoords="offset points",
        ha="right",
        va="top",
        animated=True,
    )

    cx.add_basemap(
        ax, crs=crs_projection, attribution="", source=cx.providers.Esri.WorldGrayCanvas
    )

    routes = []

    # colors
    NUM_COLORS = len(combined_gpx_attributes["routes"])
    cm = plt.get_cmap("turbo")
    cNorm = colors.Normalize(vmin=0, vmax=NUM_COLORS - 1)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(NUM_COLORS)])

    for route in combined_gpx_attributes["routes"]:
        (l,) = ax.plot([], [], "o", ls="-", markevery=[-1], mfc="red", mec="blue")

        pointsLon = []
        pointsLat = []
        for point in route["points"]:
            pointsLon.append(point["lon"])
            pointsLat.append(point["lat"])

        points = np.array([pointsLon, pointsLat])
        routes.append(
            {
                "line": l,
                "points": points,
                "time_segment_indexes": route["time_segment_indexes"],
                "last_step": route["last_step"],
                "has_marker": True,
                "fp": route["fp"],
            }
        )

    fps = 30
    video_time_limit_seconds = 300
    something = video_time_limit_seconds * fps
    bucket = 5
    max_frames = int((combined_gpx_attributes["last_step"] / bucket) + 2)
    while max_frames >= something:
        bucket += 1
        max_frames = int((combined_gpx_attributes["last_step"] / bucket) + 2)

    print(max_frames)

    anim = animation.FuncAnimation(
        fig,
        updateline,
        fargs=(fr_number, routes, max_frames, bucket),
        frames=(max_frames),
    )

    writervideo = animation.FFMpegWriter(fps=fps)
    anim.save(
        "tester.mp4",
        writer=writervideo,
    )
    print(f"total routes: {len(combined_gpx_attributes['routes'])}")
