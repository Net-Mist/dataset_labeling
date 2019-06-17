import os
import threading
from flask import Flask, url_for, redirect, Response, jsonify

image_provider = None


class ImageProvider:
    def __init__(self, img_dir: str, annotation_dir: str):
        """class providing path of images to process
        
        Args:
            img_dir (str): dir containing the images
            annotation_dir (str): dir containing the annotation files : one json per images
        """
        self.img_dir = img_dir
        self.image_list = os.listdir(self.img_dir)
        self.annotation_dir = annotation_dir

        self.lock = threading.Lock
        self.current_image = 0

        # Create annotation dir if doesn't exist
        os.makedirs(self.annotation_dir, exist_ok=True)
        self.annotation_files = os.listdir(self.annotation_dir)

        if os.path.exists(processed_image_file):
            for image in image_list:
                if image.split("."):
                    pass
            # TODO continue

    def get_image(self):
        with self.lock:
            image = self.image_list[self.current_image]
            self.current_image += 1
        return image


app = Flask(__name__)


@app.route("/get_image")
def get_image():
    pass


@app.route("/set_image")
def set_image():
    pass


def main():
    global image_provider
    image_provider = ImageProvider()
    image_provider.start()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
