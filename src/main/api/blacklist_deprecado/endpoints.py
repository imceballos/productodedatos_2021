"""API endpoint definitions for /auth namespace."""
from http import HTTPStatus
from PIL import Image
import base64
from flask_restx import Namespace, Resource
from flask import after_this_request, jsonify


from main.api.blacklist_deprecado.dto import (
    image_0_reqparser,
    image_1_reqparser,
    image_2_reqparser,
    image_3_reqparser

)
from main.api.blacklist_deprecado.business import (
    get_entry_by_id,
    get_by_confidence,
    process_image,
    get_objects_classified
)

imagentry_ns = Namespace(name="EntryImages", validate=True)

@imagentry_ns.route("/getentrybyid", endpoint="get_by_id")
class GetForSite(Resource):
    """Handles HTTP requests to URL: /entryimages/getentrybyid"""

    @imagentry_ns.expect(image_0_reqparser)
    @imagentry_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @imagentry_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @imagentry_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Get entry data of an image by id"""
        request_data = image_0_reqparser.parse_args()
        id = request_data.get("id")
        return get_entry_by_id(id)


@imagentry_ns.route("/predict", endpoint="predict_image")
class GetForSiteOne(Resource):
    """Handles HTTP requests to URL: /entryimages/predict"""

    @imagentry_ns.expect(image_1_reqparser)
    @imagentry_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @imagentry_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @imagentry_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Get the clasification of objects by a confidence, returns an image"""
        request_data = image_1_reqparser.parse_args()
        confidence = request_data.get("confidence")
        file = request_data.get("file")
        converted_string = base64.b64encode(file.read())
        return process_image(converted_string, confidence, file.filename)


@imagentry_ns.route("/countObject", endpoint="count_objects")
class GetForSiteOne(Resource):
    """Handles HTTP requests to URL: /entryimages/countObjects"""

    @imagentry_ns.expect(image_2_reqparser)
    @imagentry_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @imagentry_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @imagentry_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Get the count of differents objects"""
        request_data = image_2_reqparser.parse_args()
        confidence = request_data.get("confidence")
        file = request_data.get("file")
        element_required = request_data.get("element")
        converted_string = base64.b64encode(file.read())
        return get_objects_classified(converted_string, confidence, file.filename, element_required)




@imagentry_ns.route("/countOranges", endpoint="count_oranges")
class GetForSiteTwo(Resource):
    """Handles HTTP requests to URL: /entryimages/countOranges"""

    @imagentry_ns.expect(image_3_reqparser)
    @imagentry_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @imagentry_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @imagentry_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Get count of oranges"""
        request_data = image_3_reqparser.parse_args()
        confidence = request_data.get("confidence")
        file = request_data.get("file")
        converted_string = base64.b64encode(file.read())
        return get_objects_classified(converted_string, confidence, file.filename, "orange")
