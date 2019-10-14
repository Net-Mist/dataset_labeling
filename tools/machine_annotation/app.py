import os
import logging
import json
import coloredlogs
import cv2
import tensorflow as tf
import numpy as np
from tqdm import tqdm  # progress bar
from distribute_config import Config
# Run a frozen model on a set of images and output the detections as .json files, one per image.
# For now it only keeps "detection_classes" == 1, i.e. "class"="person"

coloredlogs.install(level="DEBUG")

Config.define_str("model_path", "/opt/model/frozen_inference_graph.pb", "Path of the model to load and execute, for instance"
                                "/opt/model/frozen_inference_graph.pb. If you're using docker-compose you shouldn't change this.")
Config.define_str("input_dir",  "", "Path where the images to annotate are stored")
Config.define_str("output_dir", "", "Path to store pre-annotations (model annotations to help human annotators)")
with Config.namespace("class"):
    Config.define_str_list("names", [], "name of the classes to annotate")
with Config.namespace("object_detection"):
    Config.define_float("threshold", 0.2, "Discard boxes with score below this value")
    Config.define_float("max_width", 1.0, "Discard boxes with width upper this value because in some cases, very large detections are mostly false positives")


def main():
    Config.load_conf()
    config = Config.get_dict()
    assert config["model_path"] != "", "model_path can't be empty"
    assert config["input_dir"] != "", "input_dir can't be empty"
    assert config["output_dir"] != "", "output_dir can't be empty"

    os.makedirs(config["output_dir"], exist_ok=True)
    images_list = os.listdir(config["input_dir"])
    annotations_list = os.listdir(config["output_dir"])

    # Only keep images that aren't processed yet
    new_list = []
    annotation_ids = [os.path.splitext(file_name)[0] for file_name in annotations_list]
    for image_name in images_list:
        image_id, _ = os.path.splitext(image_name)
        if image_id not in annotation_ids:
            new_list.append(image_name)
    images_list = new_list
    images_list.sort()
    logging.info("there are {} images to annotate".format(len(images_list)))

    # load tensorflow model (must be a frozen model)
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(config["model_path"], 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    with tf.Session() as session:
        # Get all tensors
        ops = tf.get_default_graph().get_operations()
        all_tensor_names = {output.name for op in ops for output in op.outputs}
        tensor_dict = {}
        for key in ['num_detections', 'detection_boxes', 'detection_scores', 'detection_classes']:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
        image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

        # Run inference
        first_iter = True
        for image_id in tqdm(range(len(images_list))):
            image = cv2.cvtColor(cv2.imread(os.path.join(config["input_dir"], images_list[image_id])), cv2.COLOR_BGR2RGB)

            if first_iter:
                logging.info(f"image.shape: {image.shape}")
                first_iter = False
            height, width = image.shape[:2]
            image_expanded = np.expand_dims(image, axis=0)
            output_dict = session.run(tensor_dict, feed_dict={image_tensor: image_expanded})

            good_rectangles = []
            for i, detection_score in enumerate(output_dict["detection_scores"][0]):
                if detection_score >= config["object_detection"]["threshold"]:
                    box = output_dict["detection_boxes"][0][i]  # ymin, xmin, ymax, xmax
                    if box[3]-box[1] < config["object_detection"]["max_width"]:
                        good_rectangles.append({"xMin": int(box[1] * width),
                                                "yMin": int(box[0] * height),
                                                "xMax": int(box[3] * width),
                                                "yMax": int(box[2] * height),
                                                "detection_score": detection_score.item(),
                                                "class": config["class"]["names"][int(output_dict["detection_classes"][0][i])-1]})
                else:
                    break

            json_name = os.path.splitext(images_list[image_id])[0] + ".json"
            with open(os.path.join(config["output_dir"], json_name), 'w') as outfile:
                json.dump({"rectangles": good_rectangles}, outfile)


if __name__ == "__main__":
    main()
