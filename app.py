import os
import threading
import json
import logging
import coloredlogs
from PIL import Image

from flask import Flask, url_for, redirect, Response, jsonify
from flask_cors import CORS

import flask
from absl import flags
from absl import app as absl_app

coloredlogs.install(level='DEBUG')

flags.DEFINE_string("images_path", "static/images", "Path where are stored the images to annotate")
flags.DEFINE_string("human_annotations_path", "static/human_annotations", "Path where are stored human annotation")
flags.DEFINE_string("model_annotations_path", "static/model_annotations", "Path where are stored model annotation for helping human")
flags.DEFINE_list("class_names", None, "name of the classes to annotate")
flags.DEFINE_list("class_colors", [], "colors for each classes")

flags.mark_flag_as_required('class_names')

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
        self.images_list.sort()
        self.n_images = len(self.images_list)

    def get_image(self):
        if self.current_image >= self.n_images: # all images done
            return jsonify({
                "image_path": "static/all-done__pang-yuhao-1133167-unsplash_light.jpg",
                "data": {},
                "width": 1224,
                "height": 816,
                "image_id": "All done!",
                "n_images": self.n_images})

        with self.lock:
            image = self.images_list[self.current_image]
            image_id = self.current_image
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

        return jsonify({"image_path": image_path,
                        "data": data, 
                        "width": width, 
                        "height": height,
                        "image_id": image_id,
                        "n_images": self.n_images})


app = Flask(__name__)
CORS(app)

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

    for shape in message["detectedObjects"]:
        assert shape["class"] in FLAGS.class_names

    json_name = os.path.splitext(os.path.split(message['imageSrc'])[1])[0] + ".json"

    with open(os.path.join(FLAGS.human_annotations_path, json_name), 'w') as outfile:
        json.dump({"rectangles": message["detectedObjects"]}, outfile)

    return "ok"

@app.route("/get_classes")
def get_classes():
    logging.info(FLAGS.class_names) 
    return jsonify({"classNames": FLAGS.class_names, "classColors": FLAGS.class_colors})

def main(argv):
    global image_provider
    image_provider = ImageProvider()

    # Write txt file containing class info
    with open(os.path.join(FLAGS.human_annotations_path, "class_names.txt"), "w") as f:
        f.write(','.join(FLAGS.class_names))


    app.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    absl_app.run(main)
