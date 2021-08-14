"""API blueprint configuration."""
from http import HTTPStatus
from flask import Blueprint, current_app
from flask_restx import Api

from main.api.blacklist_deprecado.endpoints import imagentry_ns

from main.exceptions import (
    NotFound,
    ServiceUnavailable,
    InternalServerError,
)

api_bp = Blueprint("api", __name__)
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="1.0",
    title="Rest API Scaffold",
    description="Welcome to the Swagger UI documentation site!",
    doc="/api/1/ui",
    authorizations=authorizations,
)

api.add_namespace(imagentry_ns, path="/entryimages")


@api.errorhandler(NotFound)
def not_found_handler(error):
    current_app.logger.error(str(error))
    return (
        {"message": error.message, "details": str(error)},
        HTTPStatus.BAD_REQUEST,
    )


@api.errorhandler(ServiceUnavailable)
def service_unavailable_handler(error):
    current_app.logger.error(str(error))
    return (
        {"message": error.message, "details": str(error)},
        HTTPStatus.SERVICE_UNAVAILABLE,
    )


@api.errorhandler(InternalServerError)
def internal_server_error_handler(error):
    current_app.logger.error(str(error))
    return (
        {"message": error.message, "details": str(error)},
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )
