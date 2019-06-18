import os
import threading
import json
import logging
import coloredlogs
from PIL import Image

from flask import Flask, url_for, redirect, Response, jsonify
import flask
from absl import flags
from absl import app as absl_app

coloredlogs.install(level='DEBUG')

flags.DEFINE_string("images_path", None, "Path where are stored the images to annotate")
flags.DEFINE_string("human_annotations_path", None, "Path where are stored human annotation")
flags.DEFINE_string("model_annotations_path", None, "Path where are stored model annotation for helping human")

flags.mark_flag_as_required('images_path')
flags.mark_flag_as_required('human_annotations_path')

FLAGS = flags.FLAGS

image_provider = None


class ImageProvider:
    def __init__(self):
        """class providing path of images to process
        """
        # user-provided attributes
        self.images_path = FLAGS.images_path
        self.human_annotations_path = FLAGS.human_annotations_path
        self.model_annotations_path = FLAGS.model_annotations_path

        # other attributes
        self.lock = threading.Lock()
        self.current_image = 0

        # Handle paths
        assert os.path.exists(self.images_path)
        os.makedirs(self.human_annotations_path, exist_ok=True)
        if self.model_annotations_path:
            os.makedirs(self.model_annotations_path, exist_ok=True)

        # Handle lists
        self.images_list = os.listdir(self.images_path)
        self.human_annotations_list = os.listdir(self.human_annotations_path)
        if self.model_annotations_path:
            self.model_annotations_list = os.listdir(self.model_annotations_path)
        else:
            self.model_annotations_list = []
        logging.info(f"there are {len(self.images_list)} images in total")

        # Only keep images that where not yet processed
        new_list = []
        human_annotation_ids = [os.path.splitext(file_name)[0] for file_name in self.human_annotations_list]
        for image_name in self.images_list:
            image_id, _ = os.path.splitext(image_name)
            if image_id not in human_annotation_ids:
                new_list.append(image_name)
        self.images_list = new_list
        logging.info(f"there are {len(self.images_list)} images to annotate")

    def get_image(self):
        with self.lock:
            image = self.images_list[self.current_image]
            self.current_image += 1

        image_path = os.path.join(self.images_path, image)
        # Get image size
        pil_image = Image.open(image_path)
        width, height = pil_image.size

        json_file_name = f"{os.path.splitext(image)[0]}.json"
        if json_file_name in self.model_annotations_list:
            with open(os.path.join(self.model_annotations_path, json_file_name), "r") as read_file:
                data = json.load(read_file)
        else:
            data = {}

        return jsonify({"image_path": image_path, "data": data, "width": width, "height": height})


app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for('static', filename='index.html'))


@app.route("/get_image")
def get_image():
    global image_provider
    logging.info("route get_image called")
    return image_provider.get_image()


@app.route("/set_image", methods=['POST'])
def set_image():
    message = flask.request.get_json()
    logging.info(message)

    json_name = os.path.splitext(os.path.split(message['image_src'])[1])[0] + ".json"

    with open(os.path.join(FLAGS.human_annotations_path, json_name), 'w') as outfile:  
        json.dump({"rectangles": message["rectangles"]}, outfile)

    return "ok"


def main(argv):
    global image_provider
    image_provider = ImageProvider()
    app.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    absl_app.run(main)
