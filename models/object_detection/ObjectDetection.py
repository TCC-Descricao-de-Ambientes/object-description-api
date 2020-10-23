######## Image Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 1/15/18
# Description:
# This program uses a TensorFlow-trained neural network to perform object detection.
# It loads the classifier and uses it to perform object detection on an image.
# It draws boxes, scores, and labels around the objects of interest in the image.

## Some of the code is copied from Google's example at
## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

## and some is copied from Dat Tran's example at
## https://github.com/datitran/object_detector_app/blob/master/object_detection_app.py

## but we changed it to make it more understandable to us.

# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import json

from .DetectedObjects import DetectedObjects


CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(
    CWD_PATH,
    "neural_network",
    "graph.pb",
)

PATH_TO_LABELS = os.path.join(
    CWD_PATH,
    "neural_network",
    "labels.json",
)


class ObjectDetection:
    def __init__(self, path: str, json: bool = True):
        self._path = path
        self._json = json
        self._load_category_index()

    def _load_category_index(self):
        with open(PATH_TO_LABELS, "r") as f:
            self.category_index = json.load(f)

    def _load_tensorflow(self):
        # Load the Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, "rb") as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name="")

            self.sess = tf.Session(graph=detection_graph)

        # Input tensor is the image
        self.image_tensor = detection_graph.get_tensor_by_name("image_tensor:0")

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = detection_graph.get_tensor_by_name("detection_boxes:0")

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name("detection_scores:0")
        self.detection_classes = detection_graph.get_tensor_by_name(
            "detection_classes:0"
        )

        # Number of objects detected
        self.num_detections = detection_graph.get_tensor_by_name("num_detections:0")

    def run(self):
        self._load_tensorflow()
        # expand image dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        image = cv2.imread(self._path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_expanded = np.expand_dims(image_rgb, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
            [
                self.detection_boxes,
                self.detection_scores,
                self.detection_classes,
                self.num_detections,
            ],
            feed_dict={self.image_tensor: image_expanded},
        )
        self.sess.close()
        objects = DetectedObjects(
            boxes, scores, classes, num, self.category_index, self._path, image.shape
        )
        return objects.to_json() if self._json else objects
