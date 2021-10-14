import os
import tensorflow as tf
import cv2
import time
import numpy as np

yolov4_path="../saved_models/yolov4/"
confthres=0.7
nmsthres=0.1

class yolo_model:
    def __init__(self, labels_path, config_path, weights_path):
        self.labels = self.get_labels(labels_path)
        self.config = self.get_config(config_path)
        self.weights = self.get_weights(weights_path)
        self.nets = self.load_model(self.config, self.weights)
    
    def get_labels(labels_path):
        # load the LPR object class labels our YOLOv4 model was trained on
        lpath=os.path.sep.join([yolov4_path, labels_path])
        LABELS = open(lpath).read().strip().split("\n")

        return LABELS

    def get_weights(weights_path):
        # derive the paths to the YOLOv4 weights
        wpath = os.path.sep.join([yolov4_path, weights_path])

        return wpath

    def get_config(config_path):
        # derive the paths to the YOLOv4 configuration
        cfg_path = os.path.sep.join([yolov4_path, config_path])

        return cfg_path

    def load_model(cfg_path, weights_path):
        # load YOLOv4 object detector
        print("[INFO] loading YOLO from disk...")
        net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)

        return net

    def detect(self, image):
        (H, W) = image.shape[:2]

        # determine only the *output* layer names that we need from YOLOv4
        ln = self.nets.getLayerNames()
        ln = [ln[i[0] - 1] for i in self.nets.getUnconnectedOutLayers()]

        # construct a blob from the input image and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes and
        # associated probabilities
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                     swapRB=True, crop=False)
        self.nets.setInput(blob)
        start = time.time()
        layerOutputs = self.nets.forward(ln)
        end = time.time()

        # show timing information on YOLOv4
        print("[INFO] YOLv4 took {:.6f} seconds".format(end - start))

        # initialize our lists of detected bounding boxes, confidences, and
        # class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability) of
                # the current object detection
                scores = detection[5:]
                # print(scores)
                classID = np.argmax(scores)
                # print(classID)
                confidence = scores[classID]

                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > confthres:
                    # scale the bounding box coordinates back relative to the
                    # size of the image, keeping in mind that YOLO actually
                    # returns the center (x, y)-coordinates of the bounding
                    # box followed by the boxes' width and height
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # apply non-maxima suppression to suppress weak, overlapping bounding
        # boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres,
                                nmsthres)

        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                cropped_image = image[y:y+h, x:x+w]

        return cropped_image