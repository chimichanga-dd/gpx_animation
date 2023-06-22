import activity_copier
import animate
import time


def main():
    activity_copier.move_and_extract_routes()
    print("\n", "Starting Animation Creation")
    start_time = time.time()
    animate.create_animation()
    print(time.time() - start_time, "seconds")


if __name__ == "__main__":
    main()
