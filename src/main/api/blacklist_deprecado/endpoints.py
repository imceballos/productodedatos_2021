"""API endpoint definitions for /auth namespace."""
from http import HTTPStatus
from PIL import Image
import base64
from flask_restx import Namespace, Resource
from flask import after_this_request, jsonify


from main.api.blacklist_deprecado.dto import (
    image_0_reqparser,
    image_1_reqparser

)
from main.api.blacklist_deprecado.business import (
    get_entry_by_id,
    get_by_confidence,
    process_image
)

imagentry_ns = Namespace(name="EntryImages", validate=True)

@imagentry_ns.route("/getentrybyid", endpoint="get_by_id")
class GetForSite(Resource):
    """Handles HTTP requests to URL: /api/v1/blacklist."""

    @imagentry_ns.expect(image_0_reqparser)
    @imagentry_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @imagentry_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @imagentry_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Get transactional history by ip in a specific time and returns the n° of trx"""
        request_data = image_0_reqparser.parse_args()
        id = request_data.get("id")
        return get_entry_by_id(id)


@imagentry_ns.route("/predict", endpoint="predict_image")
class GetForSiteOne(Resource):
    """Handles HTTP requests to URL: /api/v1/blacklist."""

    @imagentry_ns.expect(image_1_reqparser)
    @imagentry_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @imagentry_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @imagentry_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Get transactional history by ip in a specific time and returns the n° of trx"""
        request_data = image_1_reqparser.parse_args()
        confidence = request_data.get("confidence")
        file = request_data.get("file")
        converted_string = base64.b64encode(file.read())
        return process_image(converted_string, confidence)



