import cv2, logging, os
from argparse import ArgumentParser

parser = ArgumentParser(description='Extract pictures from a video.')
parser.add_argument('--file', required=True, help='input file: video to read and split')
parser.add_argument('--extract_every', type=float, default=1000, help='Time in ms between two extracted images')
parser.add_argument('--prefix', type=str, default=None, help='prefix to the name of the images')
parser.add_argument('--outputdir', type=str, default='.', help='where to save the pictures')

def main():
    args = parser.parse_args()

    if(args.prefix is None):
        args.prefix = get_prefix(args.file)
        logging.info(f'prefix: {args.prefix}')

    frame_id = 0
    last_save = -10000
    video = cv2.VideoCapture(args.file)
    if not video.isOpened():
        raise Exception(f"Cannot open video {args.file}")
    interval_between_pic = int(video.get(cv2.CAP_PROP_FPS) * args.extract_every / 1000)

    while True:
        got_frame, img = video.read()
        if not got_frame:
            logging.info('end of video')
            break
        if(frame_id - last_save > interval_between_pic):
            picture_path = os.path.join(args.outputdir, f'{args.prefix}_{frame_id}.jpg')
            cv2.imwrite(picture_path, img)
            last_save = frame_id
            logging.info('Saving picture ' + picture_path)
        frame_id += 1

def get_prefix(file):
    basename = os.path.basename(file)
    result,_ = os.path.splitext(basename)
    return result

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    main()
