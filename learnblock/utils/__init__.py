import cv2
import os

import numpy as np
from PIL import Image

UTILSPATH = os.path.dirname(os.path.realpath(__file__))
EMOTIONSCONFIGPATH = os.path.join(UTILSPATH, "emotionsConfig")

def PILImagetoCV2Image(img):
    pil_image = img.convert('RGBA')
    open_cv_image = np.array(pil_image)
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGBA2BGRA)
    return open_cv_image

def CV2ImagetoPILImage(img):
    cv2_im = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
    # cv2_im = img[:, :, ::-1]
    return Image.fromarray(cv2_im)
