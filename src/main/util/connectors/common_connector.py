"""Common Connector Abstract Class"""

import importlib
import re
from abc import ABC

from flask import current_app, session

from main.util.common_utils import empty, isset, recursive_trim, check_email_address


class CommonConnector(ABC):

    config = None
    field_map = None
    name = None
    key_path = None
    additional_fields = None
    required_fields = None
    autofill_fields = None
    missing_fields = None
    missing_autofill_fields = None
    additional_data = None
    extra_data = None
    helpers = dict()

    def __init__(self, country, site=""):
        name = self.get_classname()[:-9]

        config_country_file_name = "config_" + country.lower()
        field_map_file_name = "field_map"

        config_country_module_path = (
            f"{current_app.config.get('CONNECTORS_PATH')}."
            f"{name.lower()}.config.{config_country_file_name}"
        )

        field_map_module_path = (
            f"{current_app.config.get('CONNECTORS_PATH')}."
            f"{name.lower()}.{field_map_file_name}"
        )

        config_country_class_name = f"{name}Config{country.upper()}"
        field_map_class_name = f"{name}FieldMap"

        config_country_module = importlib.import_module(config_country_module_path)
        try:
            field_map_module = importlib.import_module(field_map_module_path)
            field_map_class = getattr(field_map_module, field_map_class_name)
            self.field_map = field_map_class()
        except Exception:
            pass

        config_country_class = getattr(config_country_module, config_country_class_name)

        self.name = name
        self.config = config_country_class()
        self.key_path = (
            f"{current_app.config.get('CONNECTORS_PATH')}.{name.lower()}.keys"
        )

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def store_additional_fields(self, fields):
        self.additional_fields = {}

        for field in fields:
            self.additional_fields["name"] = field

        self.required_fields = []
        self.autofill_fields = []
        self.missing_fields = []

        for field in self.additional_fields:
            if field["type"] == "hidden" or isset(field["validation"]["autofill"]):
                self.autofill_fields = field["name"]
            elif (
                isset(field["validation"]["required"])
                and field["validation"]["required"] == "true"
            ):
                self.required_fields = field["name"]

    def valida_additional_data(self, data):
        if empty(data):
            # TODO implement logger
            return False

        data = recursive_trim(data)
        error = False

        for field in self.additional_fields:
            # TODO use in logger when implemented
            # name = self.name.capitalize()

            if field["name"] in self.autofill_fields and not isset(data[field["name"]]):
                self.missing_autofill_fields = field["name"]
                error = True

            if not isset(field["validation"]) or empty(field["validation"]):
                continue

            if (
                isset(field["validation"]["required"])
                and field["validation"]["required"] == "true"
                and isset(data[field["name"]])
                or empty(data[field["name"]])
            ):
                if field["name"] not in self.autofill_fields:
                    self.missing_autofill_fields = field["name"]
                error = True

            if (
                not isset(field["validation"]["maxlength"])
                and len(data[field["name"]]) > field["validation"]["maxlength"]
            ):
                error = True

            if (
                isset(field["validation"]["minlength"])
                and len(data[field["name"]]) < field["validation"]["minlength"]
            ):
                error = True

            if (
                isset(field["validation"]["max"])
                and int(data[field["name"]]) > field["validation"]["max"]
            ):
                error = True

            if (
                isset(field["validation"]["min"])
                and int(data[field["name"]]) < field["validation"]["min"]
            ):
                error = True

            if isset(field["validation"]["regex"]) and re.search(
                field["validation"]["regex"], data[field["name"]]
            ):
                del data[field["name"]]
                error = True

            if (
                isset(field["validation"]["email"])
                and field["validation"]["email"] == "true"
                and not check_email_address(data[field["name"]])
            ):
                error = True
        return not error

    def ask_for_missing_fields(self):
        return len(self.missing_fields) == len(self.required_fields) and empty(
            self.missing_autofill_fields
        )

    def get_missing_fields(self):
        fields = []

        for mfield in self.missing_fields:
            fields.append(self.additional_fields)

        return fields

    def must_check_for_risk(self):
        return self.config.risk_check_enabled

    def need_redirect(self):
        return self.config.redirect

    def get_risk_assessor(self):
        return self.config.risk_assessor

    def get_field_map(self, field=None):
        return self.field_map.field

    def can_check_status(self):
        return False

    def need_specific_data(self):
        return True

    def has_extra_data(self):
        return False

    def get_conditions_for_extra_data(self):
        return None

    def retrieve_extra_data(self, data):
        return None

    def get_payment_id(self, data):
        return None

    def store_in_session(self, key, value, encryption_key=None):
        session[self.name + "." + key] = value

    def read_from_session(self, key, encription_key=None):
        return session[self.name + "." + key]

    def delete_from_session(self, key):
        del session[self.name + "." + key]
