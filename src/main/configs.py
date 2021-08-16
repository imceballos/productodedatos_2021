import os


class BaseConfig:
    """ Base configuration """

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql://{}:{}@{}/{}".format(
        os.getenv("MYSQL_USER"),
        os.getenv("MYSQL_PASSWORD"),
        os.getenv("MYSQL_HOST"),
        os.getenv("MYSQL_DATABASE"),
    )
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_CRYPTO_KEY = b"\xe9wM\x7f\x01\xb47-\xc9\xae\x83\xd6\xb1\xc6(}|\x13\x94\xfc@\xb0\x9f\xd7U\xbd;s\x96>g\x0b"
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_MASK_SWAGGER = False
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRE_HOURS = 0
    TOKEN_EXPIRE_MINUTES = 0
    HOST = ""
    HOST_PATH = ""
  

class DevelopmentConfig(BaseConfig):
    """ Development configuration """
    ENV = "development"
