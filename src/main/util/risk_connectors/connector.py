"""Risk Connector Interface"""


class RiskConnector:
    def __init__(self, data: dict) -> bool:
        pass

    def assess(self, data: dict) -> dict:
        pass