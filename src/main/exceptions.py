class NotFound(Exception):
    message = "Resource not found"


class ServiceUnavailable(Exception):
    message = "Service is unavailable"


class InternalServerError(Exception):
    message = "Internal server error"
