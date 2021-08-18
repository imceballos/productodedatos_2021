"""Business logic for /auth API endpoints."""

from datetime import datetime, timedelta
from collections import Counter
from flask import current_app, jsonify, send_file
from main import db
from main.models.models import EntryImages, ClassificationResult
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
import numpy as np
import base64
import os

def get_classification(image_array, confidence, filename):
    new_image = EntryImages(image_array=image_array, confidence=confidence).save()
    id_mother_image = new_image.id
    with open(filename, 'wb') as decodeit:
        converted_image = base64.b64decode(image_array)
        decodeit.write(converted_image)
        img = cv2.imread(filename)
        bbox, label, conf = cv.detect_common_objects(img, confidence=confidence, model="yolov3-tiny")
        return bbox, label, conf, img


def process_image(image_array, confidence, filename):
    bbox, label, conf, img = get_classification(image_array, confidence, filename)
    output_image = draw_bbox(img, bbox, label, conf)
    cv2.imwrite(f"main/{filename}", output_image)
    return send_file(filename)


def get_objects_classified(image_array, confidence, filename, element_required):
    bbox, label, conf, _ = get_classification(image_array, confidence, filename)
    if element_required != "all":
        counter = {element_required: label.count(element_required)}
        return counter
    return Counter(label)


  
def get_entry_by_id(id):
    entries = EntryImages.get_entry_by_id(id)
    for value in entries:
        return jsonify({'id': value.id, 'confidence': float(value.confidence) })
        break

def get_by_confidence(confidence):
    return EntryImages.get_by_confidence(confidence)

def get_classification_by_id(id):
    return ClassificationResult.get_by_id(id)

def get_mother_image_byid(id_mother_image):
    return ClassificationResult.get_by_mother_id(id_mother_image)

def get_classification_by_confidence(confidence):
    return ClassificationResult.get_by_confidence(confidence)