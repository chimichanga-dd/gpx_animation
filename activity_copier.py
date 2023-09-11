import os
import csv
import shutil
import gzip
import tcx_helper as TcxHelper
from fit2gpx import Converter as FitConverter


def move_and_extract_routes(activity_csv, activity_folder, only_gpx_folder):
    if not os.path.exists(only_gpx_folder):
        os.makedirs(only_gpx_folder)

    activity_paths = {}
    fit_converter = FitConverter()

    with open(
        activity_csv,
        newline="",
    ) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",")
        for row in spamreader:
            # TODO: allow activity type to be from user input
            # '9122510895', 'May 22, 2023, 11:34:17 PM', 'Countdown', 'Run'
            activity_id, activity_type, activity_path = row[0], row[3], row[12]
            if activity_type == "Run":
                activity_paths[activity_path] = True

    # activity_paths = ["/9590173068.fit"]

    for activity_rel_fp in activity_paths:
        print(f"unpacking {activity_rel_fp}")
        if activity_rel_fp == "":
            continue

        activity_file_name = activity_rel_fp.split("/")[1]

        if activity_file_name.endswith(".tcx") or activity_file_name.endswith(
            ".tcx.gz"
        ):
            zipped_tcx_file_path = f"{activity_folder}/{activity_file_name}"
            unzipped_tcx_file_path = zipped_tcx_file_path.replace(".gz", "")
            tcx_file_name = activity_file_name.replace(".gz", "")
            gpx_file_name = tcx_file_name.replace(".tcx", ".gpx")
            output_gpx_file_path = f"{only_gpx_folder}/{gpx_file_name}"

            if activity_file_name.endswith(".tcx.gz"):
                TcxHelper.unzip(zipped_tcx_file_path, unzipped_tcx_file_path)

            TcxHelper.convert_to_gpx(unzipped_tcx_file_path, output_gpx_file_path)

        elif activity_file_name.endswith(".fit") or activity_file_name.endswith(
            ".fit.gz"
        ):
            zipped_fit_file_path = f"{activity_folder}/{activity_file_name}"
            unzipped_fit_file_path = zipped_fit_file_path.replace(".gz", "")
            fit_file_name = activity_file_name.replace(".gz", "")
            gpx_file_name = fit_file_name.replace(".fit", ".gpx")
            output_gpx_file_path = f"{only_gpx_folder}/{gpx_file_name}"

            if activity_file_name.endswith(".fit.gz"):
                # unzip
                with gzip.open(zipped_fit_file_path, "rb") as f_in:
                    with open(unzipped_fit_file_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

            fit_converter.fit_to_gpx(
                f_in=unzipped_fit_file_path, f_out=output_gpx_file_path
            )

        elif activity_file_name.endswith(".gpx") or activity_file_name.endswith(
            ".gpx.gz"
        ):
            zipped_gpx_file_path = f"{activity_folder}/{activity_file_name}"
            gpx_file_name = activity_file_name.replace(".gz", "")
            output_gpx_file_path = f"{only_gpx_folder}/{gpx_file_name}"

            if activity_file_name.endswith(".gpx.gz"):
                # unzip
                with gzip.open(zipped_gpx_file_path, "rb") as f_in:
                    with open(output_gpx_file_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy(f"{activity_folder}/{activity_file_name}", only_gpx_folder)
        else:
            print(f"skipping {activity_file_name} due to file type")
    print("done")
