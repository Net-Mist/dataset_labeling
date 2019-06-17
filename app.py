import os
import threading
import json
from flask import Flask, url_for, redirect, Response, jsonify
from absl import flags, app

flags.DEFINE_string("images_path", "", "Path where are stored the images to annotate")
flags.DEFINE_string("human_annotations_path", "", "Path where are stored human annotation")
flags.DEFINE_string("model_annotations_path", "", "Path where are stored model annotation for helping human")

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
        self.lock = threading.Lock
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

        # Only keep images that where not yet processed
        new_list = []
        human_annotation_ids = [os.path.splitext(file_name)[0] for file_name in self.human_annotations_list]
        for image_name in self.images_list:
            image_id, _ = os.path.splitext(image_name)
            if image_id not in human_annotation_ids:
                new_list.append(image_name)
        self.images_list = new_list
        
    def get_image(self):
        with self.lock:
            image = self.images_list[self.current_image]
            self.current_image += 1

        json_file_name = f"{os.path.splitext(image)[0]}.json"
        if json_file_name in self.model_annotations_path:
            with open(os.path.join(self.model_annotations_path, json_file_name), "r") as read_file:
                data = json.load(read_file)
            return image, data
        else:
            return image, {}


app = Flask(__name__)


@app.route("/get_image")
def get_image():
    global image_provider
    return image_provider.get_image()


@app.route("/set_image", methods=['POST'])
def set_image():
    pass


def main(argv):
    global image_provider
    image_provider = ImageProvider()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    app.run(main)
    
