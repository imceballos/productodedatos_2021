"""Parsers and serializers for /auth API endpoints."""
from flask_restx.inputs import ip
from flask_restx.reqparse import RequestParser
import werkzeug


image_0_reqparser = RequestParser(bundle_errors=True)
image_0_reqparser.add_argument(
    name="id", type=int, location="form", required=True, nullable=False
)

image_1_reqparser = RequestParser(bundle_errors=True)
image_1_reqparser.add_argument(
    name="confidence", type=float, location="form", required=True, nullable=False
)
image_1_reqparser.add_argument(
    name='file', type=werkzeug.datastructures.FileStorage, location='files', required=True, nullable=False
)


image_2_reqparser = RequestParser(bundle_errors=True)
image_2_reqparser.add_argument(
    name="confidence", type=float, location="form", required=True, nullable=False
)
image_2_reqparser.add_argument(
    name='file', type=werkzeug.datastructures.FileStorage, location='files', required=True, nullable=False
)

image_2_reqparser.add_argument(
    name="element", type=str, location="form", required=False, default="all", nullable=False,
)


image_3_reqparser = RequestParser(bundle_errors=True)
image_3_reqparser.add_argument(
    name="confidence", type=float, location="form", required=True, nullable=False
)
image_3_reqparser.add_argument(
    name='file', type=werkzeug.datastructures.FileStorage, location='files', required=True, nullable=False
)
