import activity_copier
import animate
import time


def main():
    strava_folder = "./strava_export"  # TODO: replace with user input
    activity_csv = f"{strava_folder}/activities.csv"
    activity_folder = f"{strava_folder}/activities"
    only_gpx_folder = "./only_gpx"  # TODO: delete after process runs
    output_video_name = "plotter"

    activity_copier.move_and_extract_routes(
        activity_csv=activity_csv,
        activity_folder=activity_folder,
        only_gpx_folder=only_gpx_folder,
    )
    print("\n", "Starting Animation Creation")
    start_time = time.time()
    animate.create_animation(
        only_gpx_folder=only_gpx_folder, output_video_name=output_video_name
    )
    print(time.time() - start_time, "seconds")


if __name__ == "__main__":
    main()
