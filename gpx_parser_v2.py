import re
import argparse
import xml.etree.ElementTree as et
import math
from datetime import datetime, timedelta


def time_in_seconds(date):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            datetime.strptime(date, fmt)
            time_object = datetime.strptime(date, fmt)
            return timedelta(
                hours=time_object.hour,
                minutes=time_object.minute,
                seconds=time_object.second,
            ).total_seconds()
        except ValueError:
            pass
    raise ValueError("no valid date format found")


def step_floor(x, base=5):
    return base * math.floor(x / base)


def parse(input, combined_gpx_attributes):
    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r"^({.*})", root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ""
    if root.tag != ns + "gpx":
        print("Unknown root found: " + root.tag)
        return
    trk = root.find(ns + "trk")
    if not trk:
        print("Unable to find trk under root")
        return
    trksegs = trk.findall(ns + "trkseg")
    if not trksegs:
        print("Unable to find trksegs under trk")
        return

    earliest_point = None

    time_bucket_end_index = {}
    last_step = -math.inf
    current_route = []
    counter = 0

    for trkseg in trksegs:
        trkpts = trkseg.findall(ns + "trkpt")
        if not trkpts:
            print("Unable to find trkpts under trkseg")
            return
        for trkpt in trkpts:
            if not trkpt:
                print("missing trkpt")
            track_point_time_element = trkpt.find(ns + "time")
            track_point = {
                "lat": float(trkpt.attrib["lat"]),
                "lon": float(trkpt.attrib["lon"]),
                "time": track_point_time_element.text,
            }

            if earliest_point is None:
                earliest_point = time_in_seconds(track_point["time"])

            elapsed_time = abs(earliest_point - time_in_seconds(track_point["time"]))
            time_bucket = step_floor(elapsed_time)

            combined_gpx_attributes["min_lat"] = min(
                combined_gpx_attributes["min_lat"], track_point["lat"]
            )
            combined_gpx_attributes["max_lat"] = max(
                combined_gpx_attributes["max_lat"], track_point["lat"]
            )
            combined_gpx_attributes["min_lon"] = min(
                combined_gpx_attributes["min_lon"], track_point["lon"]
            )
            combined_gpx_attributes["max_lon"] = max(
                combined_gpx_attributes["max_lon"], track_point["lon"]
            )
            combined_gpx_attributes["last_step"] = max(
                combined_gpx_attributes["last_step"], time_bucket
            )

            last_step = max(last_step, time_bucket)
            current_route.append(track_point)
            time_bucket_end_index[time_bucket] = counter
            counter += 1

    combined_gpx_attributes["routes"].append(
        {
            "points": current_route,
            "time_segment_indexes": time_bucket_end_index,
            "last_step": last_step,
        }
    )

    return combined_gpx_attributes
