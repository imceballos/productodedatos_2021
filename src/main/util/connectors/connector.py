"""Connector Interface"""


class Connector:
    def initialize(self, data: dict, site: str) -> bool:
        pass

    def get_initial_status(self) -> str:
        pass

    def require_additional_info(self) -> bool:
        pass

    def need_redirect(self) -> bool:
        pass

    def get_redirect_data(self, data: dict) -> str:
        pass

    def validate_provider_response(self, data: dict, validate_data: dict) -> dict:
        pass

    def process_payment(self, data: dict, payment) -> dict:
        pass

    def process_response_data(self, resp_provider, resp_site, response):
        pass

    def process_end_data(self, status: str, data: dict) -> dict:
        pass

    def process_end_response(
        self, resp_site: str, resp_provider: dict, response
    ) -> dict:
        pass
