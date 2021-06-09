from openvino.inference_engine import IECore
from face_detection import FaceDetection
import cv2
import numpy as np
import time
import os
import argparse
import shutil

PATH_DATA = "/Users/ntdat/Downloads/Data_collected_on_insta/trantieuvy_20"

# path to models
FACEDETECTION_XML_PATH = "./models/face-detection-retail-0004.xml"
FACEDETECTION_BIN_PATH = "./models/face-detection-retail-0004.bin"

ie = IECore()

# Create FaceDetection model
facedetection = FaceDetection(ie, FACEDETECTION_XML_PATH, FACEDETECTION_BIN_PATH)

list_dir = os.listdir(PATH_DATA)
try:
    os.mkdir(PATH_DATA + "_cropped")
    os.mkdir(PATH_DATA + "_delete")
except Exception as ex:
    print(ex)

for img_name in list_dir:
    try:
        path_img = os.path.join(PATH_DATA, img_name)
        frame = cv2.imread(path_img)
        h, w, c = frame.shape

        frame_copy = frame.copy()

        # get face on frame
        outputs = facedetection.detect(frame)

        count = 0
        for output in outputs:
            x_min, y_min, x_max, y_max = (output * [w, h, w, h]).astype(int)

            if x_max - x_min > y_max - y_min:
                y_max += ((x_max - x_min) - (y_max - y_min)) / 2
                y_min -= ((x_max - x_min) - (y_max - y_min)) / 2
                y_min = 0 if y_min < 0 else int(y_min)
                y_max = h if y_max > h else int(y_max)
            else:
                x_max += ((y_max - y_min) - (x_max - x_min)) / 2
                x_min -= ((y_max - y_min) - (x_max - x_min)) / 2
                x_min = 0 if x_min < 0 else int(x_min)
                x_max = w if x_max > w else int(x_max)

            # crop face
            img_cropped = frame[y_min:y_max, x_min:x_max]

            cv2.imwrite(os.path.join(PATH_DATA + "_cropped", str(count) + img_name), img_cropped)

            img_cropped = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)

            color = (0, 255, 0)
            cv2.rectangle(frame_copy, (x_min, y_min), (x_max, y_max), color=color)

            count += 1

        if len(outputs) != 1:
            path_move = os.path.join(PATH_DATA + "_delete",
                                     img_name.split(".")[0] + "_" + str(len(outputs)) + ".jpg")
            if len(outputs):
                cv2.imwrite(path_move, frame_copy)
            else:
                shutil.move(path_img, path_move)
    except Exception as ex:
        print(ex)