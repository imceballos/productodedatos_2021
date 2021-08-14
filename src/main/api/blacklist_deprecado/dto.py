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


black_2_reqparser = RequestParser(bundle_errors=True)
black_2_reqparser.add_argument(
    name='file', type=werkzeug.datastructures.FileStorage, location='files', required=True, nullable=False
)
black_2_reqparser.add_argument(
    name="site_id", type=int, location="form", required=True, nullable=False
)

black_3_reqparser = RequestParser(bundle_errors=True)
black_3_reqparser.add_argument(
    name="site_id", type=int, location="form", required=True, nullable=False
)
black_3_reqparser.add_argument(
    name="site_id", type=int, location="form", required=True, nullable=False
)
black_3_reqparser.add_argument(
    name="ip_address", type=ip, location="form", required=True, nullable=False
)


black_4_reqparser = RequestParser(bundle_errors=True)
black_4_reqparser.add_argument(
    name="site_id", type=int, location="form", required=True, nullable=False
)
black_4_reqparser.add_argument(
    name="ip_address", type=ip, location="form", required=True, nullable=False
)
