"""Risk Common Connector Abstract Class"""

import importlib
from abc import ABC
from flask import current_app


class RiskCommonConnector(ABC):

    name = None
    country = None
    key_path = None
    config = None
    iovation_blackbox = ""

    def __init__(self, country):
        name = self.get_classname()[:-13]

        config_country_file_name = "config_" + country.lower()
        config_country_module_path = (
            f"{current_app.config.get('RISK_CONNECTORS_PATH')}."
            f"{name.lower()}.config.{config_country_file_name}"
        )

        config_country_class_name = f"{name}Config{country.upper()}"
        config_country_module = importlib.import_module(config_country_module_path)
        config_country_class = getattr(config_country_module, config_country_class_name)

        self.name = name
        self.country = country
        self.config = config_country_class()
        self.key_path = (
            f"{current_app.config.get('RISK_CONNECTORS_PATH')}.{name.lower()}.keys"
        )

    def set_iovation_blackbox(self, blackbox):
        self.iovation_blackbox = blackbox

    @classmethod
    def get_classname(cls):
        return cls.__name__
