# Dataset labeling

## Start the annotation service using docker
You need to specified the folder containing the images to label, the folder containing the human annotations and the folder containing the 
model annotations. You also need to specified at least one class name. If you want specific color for the bounding box you can specified a list of same size than the 
class_name list

These paths can be given to docker using env variables:
-  IMAGES_PATH
-  HUMAN_ANNOTATIONS_PATH
-  MODEL_ANNOTATIONS_PATH
-  CLASS_NAMES
-  CLASS_COLORS

then you can start the serving doing `docker-compose up`

for instance, for testing purposes:
```bash
export IMAGES_PATH=$(pwd)/assets/images
export HUMAN_ANNOTATIONS_PATH=$(pwd)/assets/human_annotations
export MODEL_ANNOTATIONS_PATH=$(pwd)/assets/model_annotations
export CLASS_NAMES=truck,red,orange,black
export CLASS_COLORS=#e5ff00,#ff0000,#ff7f00,#000000  
docker-compose up 
```

Please note than a file "class_names.txt" will be created in MODEL_ANNOTATIONS_PATH with the list of the cass names. This file is useful for the next step : 
generating the tfrecord files

## Start the annotation service without docker
If everything is installed on your host computer, you can start the annotation service by running:

```bash
python3 app.py --images_path= \
               --human_annotations_path= \
               --model_annotations_path=
```

the images need to be in the static folder to be served with flask
