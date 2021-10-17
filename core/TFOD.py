import os
import tensorflow as tf
import cv2
import time
import numpy as np

from object_detection.utils import label_map_util, config_util
from object_detection.builders import model_builder

tfod_path = "saved_models/tfod"

class tfod_model:
    def __init__(self, labels_path, config_path, ckpt_path):
        self.labels = self.get_labels(labels_path)
        self.config = self.get_config(config_path)
        self.nets = self.load_model(self.config)
        self.ckpt = self.get_ckpt(ckpt_path, self.nets)
    
    def get_labels(self, labels_path):
        lpath = os.path.sep.join([tfod_path, labels_path])
        LABELS = label_map_util.create_category_index_from_labelmap(lpath)

        return LABELS

    def get_config(self, config_path):
        cfg_path = os.path.join(tfod_path, config_path)
        CFG = config_util.get_configs_from_pipeline_file(cfg_path)

        return CFG

    def load_model(self, configs):
        detection_model = model_builder.build(model_config=configs['model'], is_training=False)

        return detection_model

    def get_ckpt(self, ckpt_path, detection_model):
        ckpt_path = os.path.join(tfod_path, ckpt_path)
        ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
        ckpt.restore(ckpt_path).expect_partial()

        return ckpt
    
    @tf.function
    def detect(self, image):
        image, shapes = self.nets.preprocess(image)
        prediction_dict = self.nets.predict(image, shapes)
        detections = self.nets.postprocess(prediction_dict, shapes)

        return detections

    def get_digits_lpr(self, detections):
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                      for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        label_id_offset = 1
        # image_np_with_detections = image_np.copy()
        boxes = detections['detection_boxes']
        max_boxes_to_draw = 8
        scores = detections['detection_scores']
        class_idx = detections['detection_classes'] + label_id_offset
        min_score_thresh = 0.5

        result = []
        for i in range(min(max_boxes_to_draw, boxes.shape[0])):
            if scores[i] > min_score_thresh:
                item = {"label": self.labels[class_idx[i]]["name"],
                        "score": scores[i],
                        "boxes": boxes[i][1]
                        }
                result.append(item)

        result = sorted(result, key=lambda k: k['boxes'])
        digit_plate = ""
        for digit in result:
            digit_plate = digit_plate + digit["label"]
        
        return digit_plate