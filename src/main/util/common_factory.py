"""Business logic for /commonFactory API endpoints."""

import importlib
import inflection
from flask import current_app


class CommonFactory:
    """Common class factory

    Keyword arguments:
    name -- Class name, case sensitive!
    country -- Country code, ex 'CO'
    site -- No clue
    type_connector -- Example, 'connectors'
    Return: Class object
    """

    @staticmethod
    def create(name, country, site, type_connector):
        if name == "" or type_connector == "":
            return None
        type_singularized = inflection.singularize(type_connector)
        path = current_app.config.get(f"{type_connector.upper()}_PATH")
        module_path = f"{path}.{name.lower()}.{type_singularized}"
        class_name = f"{name.capitalize()}{type_singularized.capitalize()}"
        
        try:
            module = importlib.import_module(module_path)
            class_ = getattr(module, class_name)
            return class_(country, site)
        except Exception as e:
            current_app.logger.error(f"Class factory error:{str(e)}")
            return None
