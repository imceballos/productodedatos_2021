"""Installation script for flask-api-tutorial application."""
from pathlib import Path

from setuptools import setup, find_packages

DESCRIPTION = ""
APP_ROOT = Path(__file__).parent
AUTHOR = ""
AUTHOR_EMAIL = ""
PROJECT_URLS = {
    "Documentation": "",
    "Bug Tracker": "",
    "Source Code": "",
}
INSTALL_REQUIRES = [
    "Flask==1.0.2",
    "gunicorn==19.9.0",
    "inflection==0.5.1",
    "requests==2.21.0",
    "Flask-SQLAlchemy",
    "Flask-Migrate==2.5.3",
    "Flask-RESTful==0.3.9",
    "Flask-Marshmallow==0.13.0",
    "flask-restx==0.2.0",
    "Flask-Cors==3.0.8",
    "Flask-Bcrypt==0.7.1",
    "Flask-Caching==1.9.0",
    "marshmallow-sqlalchemy==0.23.1",
    "mysqlclient",
    "python-dotenv",
    "pycryptodome",
    "py3rijndael",
    "jinja2",
    "redis==3.5.3",
    "Pillow",
    "cvlib==0.2.5",
    "tensorflow==2.3.1",
    "opencv-python-headless==4.4.0.46"

]
EXTRAS_REQUIRE = {"dev": ["pytest", "pytest-flask", "pytest-clarity"]}

setup(
    name="flask-api-scaffold",
    description=DESCRIPTION,
    version="1.0",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license="MIT",
    url="",
    project_urls=PROJECT_URLS,
    packages=find_packages(where="main/"),
    package_dir={"": "main/"},
    python_requires=">=3.7",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)
