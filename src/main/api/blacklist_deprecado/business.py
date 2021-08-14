"""Business logic for /auth API endpoints."""

from datetime import datetime, timedelta

from flask import current_app, jsonify, send_file
from main import db
from main.models.models import EntryImages, ClassificationResult
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
import numpy as np
import base64
import os


def process_image(image_array, confidence):

    new_image = EntryImages(image_array=image_array, confidence=confidence)
    db.session.add(new_image)
    db.session.commit()
    id_mother_image = new_image.id
    with open('hello_level.jpg', 'wb') as decodeit:
        converted_image = base64.b64decode(image_array)
        decodeit.write(converted_image)
        img = cv2.imread('hello_level.jpg')
        bbox, label, conf = cv.detect_common_objects(img, confidence=confidence, model="yolov3-tiny")
        for b,l,c in zip(bbox, label, conf):
            new_clasification = ClassificationResult(id_mother_image = id_mother_image,box = str(b), confidence = c)
            db.session.add(new_clasification)
            db.session.commit()


    output_image = draw_bbox(img, bbox, label, conf)
    cv2.imwrite("main/fermadad.jpg", output_image)

    return send_file("fermadad.jpg")

  
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