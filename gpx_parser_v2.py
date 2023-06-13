import re
import xml.etree.ElementTree as et
import math
from datetime import datetime, timedelta


def get_datetime(date):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            datetime.strptime(date, fmt)
            time_object = datetime.strptime(date, fmt)
            return time_object
        except ValueError:
            pass
    raise ValueError("no valid date format found")


def diff_between(date1, date2):
    return (get_datetime(date1) - get_datetime(date2)).total_seconds()


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

    temp_min_lat = math.inf
    temp_max_lat = -math.inf
    temp_min_lon = math.inf
    temp_max_lon = -math.inf
    temp_last_step = 0

    sf_boundary_long = (-122.5285460125, -122.3569265964)
    sf_boundary_lat = (37.8445401679, 37.6875447784)
    is_inside_sf = False

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
                earliest_point = track_point["time"]

            elapsed_time = abs(diff_between(earliest_point, track_point["time"]))
            time_bucket = step_floor(elapsed_time)

            temp_min_lat = min(temp_min_lat, track_point["lat"])
            temp_max_lat = max(temp_max_lat, track_point["lat"])
            temp_min_lon = min(temp_min_lon, track_point["lon"])
            temp_max_lon = max(temp_max_lon, track_point["lon"])
            temp_last_step = max(temp_last_step, time_bucket)

            if (
                track_point["lon"] > sf_boundary_long[0]
                and track_point["lon"] < sf_boundary_long[1]
                and track_point["lat"] < sf_boundary_lat[0]
                and track_point["lat"] > sf_boundary_lat[1]
            ):
                is_inside_sf = True

            last_step = max(last_step, time_bucket)
            current_route.append(track_point)
            time_bucket_end_index[time_bucket] = counter
            counter += 1

    if not is_inside_sf:
        return

    combined_gpx_attributes["min_lat"] = min(
        combined_gpx_attributes["min_lat"], temp_min_lat
    )
    combined_gpx_attributes["max_lat"] = max(
        combined_gpx_attributes["max_lat"], temp_max_lat
    )
    combined_gpx_attributes["min_lon"] = min(
        combined_gpx_attributes["min_lon"], temp_min_lon
    )
    combined_gpx_attributes["max_lon"] = max(
        combined_gpx_attributes["max_lon"], temp_max_lon
    )
    combined_gpx_attributes["last_step"] = max(
        combined_gpx_attributes["last_step"], temp_last_step
    )
    combined_gpx_attributes["routes"].append(
        {
            "points": current_route,
            "time_segment_indexes": time_bucket_end_index,
            "last_step": last_step,
            "fp": input,
        }
    )

    return combined_gpx_attributes
