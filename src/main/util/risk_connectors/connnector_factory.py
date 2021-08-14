"""Risk Connector Factory"""

from main.util.common_factory import CommonFactory


class RiskConnectorFactory(CommonFactory):
    @staticmethod
    def create(name, country, site_name="", type_connector="risk_connectors"):
        return CommonFactory.create(name, country, site_name, type_connector)
