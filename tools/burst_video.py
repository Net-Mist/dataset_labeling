import cv2
import logging
import os
import coloredlogs
from distribute_config import Config

coloredlogs.install(level="DEBUG")

Config.define_str("file", "", "input file: video to read and split")
Config.define_float("extract_every", 100, "Time in ms between two extracted images")
Config.define_str("prefix", "", "Prefix to the name of the images")
Config.define_str("outputdir", ".", "Where to save the pictures")


def main():
    Config.load_conf("config_video_burst.yml")
    config = Config.get_dict()

    # check if the script can run
    assert os.path.isfile(config["file"]), f"Option 'file' need to be provided"
    os.makedirs(config["outputdir"], exist_ok=True)

    if(config["prefix"] == ""):
        config["prefix"] = get_prefix(config["file"])
        logging.info(f'prefix: {config["prefix"]}')

    frame_id = 0
    last_save = -10000
    video = cv2.VideoCapture(config["file"])
    if not video.isOpened():
        raise Exception(f"Cannot open video {config['file']}")
    interval_between_pic = int(video.get(cv2.CAP_PROP_FPS) * config["extract_every"] / 1000)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    logging.info(f'frame_count: {frame_count}')
    frame_count_length = len(str(frame_count))

    while True:
        got_frame, img = video.read()
        if not got_frame:
            logging.info('end of video')
            break
        if(frame_id - last_save > interval_between_pic):
            picture_path = os.path.join(config["outputdir"], f'{config["prefix"]}_{frame_id:0{frame_count_length}}.jpg')
            cv2.imwrite(picture_path, img)
            last_save = frame_id
            logging.info('Saving picture ' + picture_path)
        frame_id += 1


def get_prefix(file):
    basename = os.path.basename(file)
    result, _ = os.path.splitext(basename)
    return result


if __name__ == "__main__":
    main()
