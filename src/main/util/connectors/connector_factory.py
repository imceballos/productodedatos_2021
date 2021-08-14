"""Connector Factory"""

from main.util.common_factory import CommonFactory


class ConnectorFactory(CommonFactory):
    @staticmethod
    def create(name, country, site_name="", type_connector="connectors"):
        return CommonFactory.create(name, country, site_name, type_connector)
