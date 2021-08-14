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
    CONNECTORS_PATH = "main.util.connectors"
    KEYS_PATH = "{}/../keys/{}"
    GROUPON_PRIVATE = "groupon.itier.{}.pem"
    GROUPON_PUBLIC = "groupon.itier.{}.pub"
    PAYMENTS_PRIVATE = "payments.pem"
    PAYMENTS_PUBLIC = "payments.pub"
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_SECRET_ID = os.getenv("PAYPAL_SECRET_ID")
    SECURITY_USE_ENCRYPTION = True
    RECAPTCHACOUNTRY = ["CL", "IL"]
    RECAPTCHATOLERANCE = 0.8
    RECAPTCHASECRET = ""
    RECAPTCHASITEKEY = ""
    CSS_PAYMENTS = os.getenv("CSS_PAYMENTS")
    RISK_ASSESSMENT = {
        "accertify": {"enableABTesting": True, "ABTestingCut": True},
        "cybersource": {"enableABTesting": True, "ABTestingCut": True},
    }
    PEIXEURBANO_DATABASE_URI = "mysql://latam-utils:aXGRhasysPiKRI4@dbuat.admingroupon.needish.local:3306/clandescuento"
    CHECKOUT_API_KEY = "cpt01W8z87soLKKwZ4QrcIMpg7ZdWd6D"
    REDIS_CONFIG = {
        "CACHE_TYPE": "redis",
        "CACHE_KEY_PREFIX": "fcache",
        "CACHE_REDIS_HOST": "uat-payment-portal.78vivq.0001.use1.cache.amazonaws.com",
        "CACHE_REDIS_PORT": "6379",
        "CACHE_REDIS_URL": "redis://uat-payment-portal.78vivq.0001.use1.cache.amazonaws.com:6379",
    }
    

class DevelopmentConfig(BaseConfig):
    """ Development configuration """

    ENV = "development"
    TOKEN_EXPIRE_HOURS = 1
    TOKEN_EXPIRE_MINUTES = 1
    TRX_TO_ADD = 30
    TRX_MINUTES_VALIDATE = 30
    TRX_WHITE_LIST = ["200.41.94.60"]
    KEYS_PATH = "{}/../keys_staging/{}"
    DEBUG = True
    SECURITY_USE_ENCRYPTION = True
    RECAPTCHASECRET = "6LfbqbAUAAAAAGdt3VVMwhLneOXsN3PBBHobzBYM"
    RECAPTCHASITEKEY = "6LfbqbAUAAAAAI42SaZakApSWp4fvDOrbmU2MK2f"
    RESPONSE_URL = "http://localhost:23006/pages/return"
    SSL_SERVER_ADDRESS  = "https://localhost:23006/api/1/"
    SERVER_ADDRESS      = "http://localhost:23006/api/1/"


class TestingConfig(BaseConfig):
    """ Testing configuration """

    TESTING = True
    KEYS_PATH = "{}/../keys_staging/{}"
    TRX_MINUTES_VALIDATE = 300
    TRX_TO_ADD = 1
    TRX_MINUTES_VALIDATE = 300
    TRX_WHITE_LIST = ["192.168.1.1"]


class StagingConfig(BaseConfig):
    """ Staging configuration """

    ENV = "stage"
    DEBUG = False
    TOKEN_EXPIRE_HOURS = 24
    TOKEN_EXPIRE_MINUTES = 60
    KEYS_PATH = "{}/../keys_staging/{}"
    SSL_SERVER_ADDRESS  = "https://localhost:23006/api/1/"
    SERVER_ADDRESS      = "http://localhost:23006/api/1/"

class ProductionConfig(BaseConfig):
    """ Production configuration """

    ENV = "production"
    DEBUG = False
    TESTING = False
    TOKEN_EXPIRE_HOURS = 24
    TOKEN_EXPIRE_MINUTES = 24
    GROUPON_PRIVATE = "groupon.itier.{}.pem"
    GROUPON_PUBLIC = "groupon.itier.{}.pub"
    PAYMENTS_PRIVATE = "payments.pem"
    PAYMENTS_PUBLIC = "payments.pub"
    REDIS_CONFIG = {
        "CACHE_TYPE": "redis",
        "CACHE_KEY_PREFIX": "fcache",
        "CACHE_REDIS_HOST": "",
        "CACHE_REDIS_PORT": "6379",
        "CACHE_REDIS_URL": "redis://:6379",
    }
    SSL_SERVER_ADDRESS  = "https://localhost:23006/api/1/"
    SERVER_ADDRESS      = "http://localhost:23006/api/1/"
