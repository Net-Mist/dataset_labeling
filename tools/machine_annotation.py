import os
import logging
import json
import coloredlogs
import cv2
import tensorflow as tf
import numpy as np
from absl import flags, app
from tqdm import tqdm # progress bar

# Run a frozen model on a set of images and output the detections as .json files, one per image.
# For now it only keeps "detection_classes" == 1, i.e. "class"="person"

coloredlogs.install(level="DEBUG")

flags.DEFINE_string("model_path", None, "Path of the model to load and execute, for instance models/frozen_inference_graph.pb")
flags.DEFINE_string("input_dir",  None, "Path where the images to annotate are stored")
flags.DEFINE_string("output_dir", None, "Path to store pre-annotations (model annotations to help human annotators)")

flags.mark_flag_as_required("model_path")
flags.mark_flag_as_required("input_dir")
flags.mark_flag_as_required("output_dir")

FLAGS = flags.FLAGS


def main(argv):
    os.makedirs(FLAGS.output_dir, exist_ok=True)
    images_list = os.listdir(FLAGS.input_dir)
    annotations_list = os.listdir(FLAGS.output_dir)

    # Only keep images that aren't processed yet
    new_list = []
    annotation_ids = [os.path.splitext(file_name)[0] for file_name in annotations_list]
    for image_name in images_list:
        image_id, ext = os.path.splitext(image_name)
        if ext.lower() not in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
            print(f'ignoring {image_name} because it has unrecognized extension {ext}')
            continue
        if image_id not in annotation_ids:
            new_list.append(image_name)
    images_list = new_list
    images_list.sort()
    logging.info("there are {} images to annotate".format(len(images_list)))

    # load tensorflow model (must be a frozen model)
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(FLAGS.model_path, 'rb') as fid:
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
            image = cv2.cvtColor(cv2.imread(os.path.join(FLAGS.input_dir, images_list[image_id])), cv2.COLOR_BGR2RGB)

            if first_iter:
                print(image.shape)
                first_iter=False
            height, width = image.shape[:2]
            image_expanded = np.expand_dims(image, axis=0)
            output_dict = session.run(tensor_dict, feed_dict={image_tensor: image_expanded})

            good_rectangles = []
            for i, detection_score in enumerate(output_dict["detection_scores"][0]):
                if detection_score > 0.2:
                    box = output_dict["detection_boxes"][0][i]  # ymin, xmin, ymax, xmax
                    if output_dict["detection_classes"][0][i] == 1 \
                       and box[3]-box[1] < 0.7 : # very large detections are mostly false positives
                        good_rectangles.append({"xMin": int(box[1] * width),
                                                "yMin": int(box[0] * height),
                                                "xMax": int(box[3] * width),
                                                "yMax": int(box[2] * height),
                                                "detection_score": detection_score.item(),
                                                "class":"person"})
                else:
                    break

            json_name = os.path.splitext(images_list[image_id])[0] + ".json"
            with open(os.path.join(FLAGS.output_dir, json_name), 'w') as outfile:
                json.dump({"rectangles": good_rectangles}, outfile)


if __name__ == "__main__":
    app.run(main)
