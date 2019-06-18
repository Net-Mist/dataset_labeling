# Dataset labeling

## Start the annotation service using docker
You need to specified the folder containing the images to label, the folder containing the human annotations and the folder containing the 
model annotations.

These paths can be given to docker using 3 env variables:
-  IMAGES_PATH
-  HUMAN_ANNOTATIONS_PATH
-  MODEL_ANNOTATIONS_PATH

then you can start the serving doing `docker-compose up`

for instance, for testing purposes:
```bash
export IMAGES_PATH=$(pwd)/assets/images
export HUMAN_ANNOTATIONS_PATH=$(pwd)/assets/human_annotations
export MODEL_ANNOTATIONS_PATH=$(pwd)/assets/model_annotations
docker-compose up 
```

## Start the annotation service without docker
If everything is installed on your host computer, you can start the annotation service by running:

```bash
python3 app.py --images_path= \
               --human_annotations_path= \
               --model_annotations_path=
```

the images need to be in the static folder to be served with flask
