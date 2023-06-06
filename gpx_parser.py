import re
import argparse
import xml.etree.ElementTree as et
import math

# takes in a GPX file and outputs a CSV file


def parse(input):
    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r'^({.*})', root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ''
    if root.tag != ns+'gpx':
        print('Unknown root found: '+root.tag)
        return
    trk = root.find(ns+'trk')
    if not trk:
        print('Unable to find trk under root')
        return
    trksegs = trk.findall(ns + "trkseg")
    if not trksegs:
        print("Unable to find trksegs under trk")
        return
    #loop over each trksegment

    gpx_attributes = {
        "min_lat": math.inf,
        "max_lat": -math.inf,
        "min_lon": math.inf,
        "max_lon": -math.inf,
        "points": [],
        "lats": [],
        "lons": []
    }

    earliest_point = None

    for trkseg in trksegs:
        trkpts = trkseg.findall(ns+'trkpt')
        if not trkpts:
            print('Unable to find trkpts under trkseg')
            return
        for trkpt in trkpts:
            if not trkpt:
                print("missing trkpt")
            # print(trkpt)
            track_point_time_element = trkpt.find(ns+'time')
            # print(track_point_time_element, track_point_time_element.text)
            track_point = {
                "lat": float(trkpt.attrib['lat']),
                "lon": float(trkpt.attrib['lon']),
                "time": track_point_time_element.text,
            }

            gpx_attributes["lats"].append(track_point["lat"])
            gpx_attributes["lons"].append(track_point["lon"])
            gpx_attributes["min_lat"] = min(gpx_attributes["min_lat"], track_point["lat"])
            gpx_attributes["max_lat"] = max(gpx_attributes["max_lat"], track_point["lat"])
            gpx_attributes["min_lon"] = min(gpx_attributes["min_lon"], track_point["lon"])
            gpx_attributes["max_lon"] = max(gpx_attributes["max_lon"], track_point["lon"])

            gpx_attributes["points"].append(track_point)
    return gpx_attributes


