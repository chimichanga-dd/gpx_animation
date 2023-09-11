import shutil
import gzip
import re
from gpx_converter import Converter
import xml.etree.ElementTree as et


def unzip(zipped_tcx_file_path, new_file_path):
    # unzip
    with gzip.open(zipped_tcx_file_path, "rb") as f_in:
        with open(new_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # remove breaking added space
    with open(new_file_path) as file:
        lines = file.readlines()
        lines[0] = '<?xml version="1.0" encoding="UTF-8" ?> \n'
    with open(new_file_path, "w") as file:
        for line in lines:
            file.write(line)


def convert_to_csv(input, output):
    tree = et.parse(input)
    root = tree.getroot()
    m = re.match(r"^({.*})", root.tag)
    if m:
        ns = m.group(1)
    else:
        ns = ""
    if root.tag != ns + "TrainingCenterDatabase":
        print("Unknown root found: " + root.tag)
        return
    activities = root.find(ns + "Activities")
    if not activities:
        print("Unable to find Activities under root")
        return
    activity = activities.find(ns + "Activity")
    if not activity:
        print("Unable to find Activity under Activities")
        return
    columnsEstablished = False
    for lap in activity.iter(ns + "Lap"):
        if columnsEstablished:
            fout.write("New Lap\n")
        for track in lap.iter(ns + "Track"):
            # pdb.set_trace()
            if columnsEstablished:
                fout.write("New Track\n")
            for trackpoint in track.iter(ns + "Trackpoint"):
                try:
                    time = trackpoint.find(ns + "Time").text.strip()
                except:
                    time = ""
                try:
                    latitude = (
                        trackpoint.find(ns + "Position")
                        .find(ns + "LatitudeDegrees")
                        .text.strip()
                    )
                except:
                    latitude = ""
                try:
                    longitude = (
                        trackpoint.find(ns + "Position")
                        .find(ns + "LongitudeDegrees")
                        .text.strip()
                    )
                except:
                    longitude = ""
                try:
                    altitude = trackpoint.find(ns + "AltitudeMeters").text.strip()
                except:
                    altitude = ""
                try:
                    bpm = (
                        trackpoint.find(ns + "HeartRateBpm")
                        .find(ns + "Value")
                        .text.strip()
                    )
                except:
                    bpm = ""
                if not columnsEstablished:
                    fout = open(output, "w")
                    fout.write(
                        ",".join(
                            (
                                "Time",
                                "LatitudeDegrees",
                                "LongitudeDegrees",
                                "AltitudeMeters",
                                "heartratebpm/value",
                            )
                        )
                        + "\n"
                    )
                    columnsEstablished = True
                fout.write(",".join((time, latitude, longitude, altitude, bpm)) + "\n")

    fout.close()


def convert_to_gpx(tcx_file_path, gpx_output_path):
    csv_path = tcx_file_path.replace("tcx", "csv")

    # remove breaking added space
    with open(tcx_file_path) as file:
        lines = file.readlines()
        lines[0] = '<?xml version="1.0" encoding="UTF-8" ?> \n'

    with open(tcx_file_path, "w") as file:
        for line in lines:
            file.write(line)

    # convert tcx to csv
    convert_to_csv(tcx_file_path, csv_path)

    # # remove blank lat longs
    with open(csv_path) as file:
        lines = file.readlines()

    with open(csv_path, "w") as file:
        for line in lines:
            splits = line.split(",")
            if len(splits) < 3:
                continue
            lat, long = splits[1], splits[2]
            if lat == "" or long == "":
                continue
            file.write(line)

    # dont make gpx from blank files
    with open(csv_path, "r") as file:
        if len(file.readlines()) < 2:
            return

    Converter(input_file=csv_path).csv_to_gpx(
        lats_colname="LatitudeDegrees",
        longs_colname="LongitudeDegrees",
        output_file=gpx_output_path,
        times_colname="Time",
    )
