import csv
import shutil
import gzip
import tcx_to_csv
from gpx_converter import Converter
from fit2gpx import Converter as FitConverter


def move_and_extract_routes():
    strava_folder = "./strava_export"
    all_activities = f"{strava_folder}/activities"
    only_runs_folder = "./only_runs"

    activity_csv = f"{strava_folder}/activities.csv"

    activity_paths = {}
    fit_converter = FitConverter()

    with open(
        activity_csv,
        newline="",
    ) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",")
        for row in spamreader:
            # '9122510895', 'May 22, 2023, 11:34:17 PM', 'Countdown', 'Run'
            activity_id, activity_type, activity_path = row[0], row[3], row[12]
            if activity_type == "Run":
                activity_paths[activity_path] = True

    for activity_rel_fp in activity_paths:
        if activity_rel_fp == "":
            continue

        print(f"Prepping {activity_rel_fp}")

        activity_file_name = activity_rel_fp.split("/")[1]

        if activity_file_name.endswith(".tcx.gz"):
            zipped_tcx_file_path = f"{all_activities}/{activity_file_name}"
            new_file_name = activity_file_name.replace(".gz", "")
            new_file_path = f"{only_runs_folder}/{new_file_name}"

            csv_path = new_file_path.replace("tcx", "csv")
            gpx_path = new_file_path.replace("tcx", "gpx")

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

            # convert tcx to csv
            tcx_to_csv.convert(new_file_path, csv_path)

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
                    continue

            Converter(input_file=csv_path).csv_to_gpx(
                lats_colname="LatitudeDegrees",
                longs_colname="LongitudeDegrees",
                output_file=gpx_path,
                times_colname="Time",
            )
        elif activity_file_name.endswith(".fit.gz"):
            zipped_tcx_file_path = f"{all_activities}/{activity_file_name}"
            unzipped_file_name = activity_file_name.replace(".gz", "")
            unzipped_file_path = f"{only_runs_folder}/{unzipped_file_name}"

            gpx_path = unzipped_file_path.replace("fit", "gpx")

            # unzip
            with gzip.open(zipped_tcx_file_path, "rb") as f_in:
                with open(unzipped_file_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            fit_converter.fit_to_gpx(f_in=unzipped_file_path, f_out=gpx_path)
        elif activity_file_name.endswith(".gpx.gz"):
            zipped_tcx_file_path = f"{all_activities}/{activity_file_name}"
            new_file_name = activity_file_name.replace(".gz", "")
            new_file_path = f"{only_runs_folder}/{new_file_name}"

            with gzip.open(zipped_tcx_file_path, "rb") as f_in:
                with open(new_file_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy(f"{all_activities}/{activity_file_name}", only_runs_folder)
    print("done")
