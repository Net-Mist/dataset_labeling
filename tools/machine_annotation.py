import os
import logging
import json
import coloredlogs
import cv2
import tensorflow as tf
import numpy as np
from absl import flags, app
from tqdm import tqdm

coloredlogs.install(level="DEBUG")

flags.DEFINE_string("model_path", "/mnt/nas/tf_experiments/vca/export_all_data_2_3/frozen_inference_graph.pb", "Path of the model to load and execute")
flags.DEFINE_string("images_path", "/mnt/nas/datasets/vca/images_batch07_all/2019-06-17", "Path where are stored the images to annotate")
flags.DEFINE_string("model_annotations_path", "/mnt/nas/datasets/vca/images_batch07_machine_annotation", "Path where are stored model annotation for helping human")


# flags.mark_flag_as_required("images_path")
# flags.mark_flag_as_required("images_path")
# flags.mark_flag_as_required("model_annotations_path")

FLAGS = flags.FLAGS


def main(argv):
    os.makedirs(FLAGS.model_annotations_path, exist_ok=True)
    images_list = os.listdir(FLAGS.images_path)
    annotations_list = os.listdir(FLAGS.model_annotations_path)

    # Only keep images that where not yet processed
    new_list = []
    annotation_ids = [os.path.splitext(file_name)[0] for file_name in annotations_list]
    for image_name in images_list:
        image_id, _ = os.path.splitext(image_name)
        if image_id not in annotation_ids:
            new_list.append(image_name)
    images_list = new_list
    logging.info(f"there are {len(images_list)} images to annotate")

    # load tensorflow model (need to be a frozen model)
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

        # Now we can run inference
        first_iter = True
        for image_id in tqdm(range(len(images_list))):
            image = cv2.cvtColor(cv2.imread(os.path.join(FLAGS.images_path, images_list[image_id])), cv2.COLOR_BGR2RGB)   
            
            if first_iter:
                print(image.shape)
                first_iter=False
            height, width = image.shape[:2]
            image_expanded = np.expand_dims(image, axis=0)
            output_dict = session.run(tensor_dict, feed_dict={image_tensor: image_expanded})

            good_rectangles = []
            for i, detection_score in enumerate(output_dict["detection_scores"][0]):
                if detection_score > 0.4:
                    box = output_dict["detection_boxes"][0][i]  # ymin, xmin, ymax, xmax
                    good_rectangles.append({"xMin": int(box[1] * width),
                                            "yMin": int(box[0] * height), 
                                            "xMax": int(box[3] * width), 
                                            "yMax": int(box[2] * height)})
                else:
                    break

            json_name = os.path.splitext(images_list[image_id])[0] + ".json"
            with open(os.path.join(FLAGS.model_annotations_path, json_name), 'w') as outfile:
                json.dump({"rectangles": good_rectangles}, outfile)


if __name__ == "__main__":
    app.run(main)
