"""Business logic for /Risk Model."""

from main.models.payments_db import RiskDataAccertify, RiskDataCybersource

from main.util.app_controller import AppController


class RiskControl(AppController):
    def __init__(self):
        AppController.__init__(self)

    def get_by_payment_accertify(self, payment_id: int):
        result = RiskDataAccertify.find_by_pid(payment_id)
        if result is None:
            return {}
        return result.recommendation_code

    def get_by_payment_cyber(self, payment_id: int):
        result = RiskDataCybersource.find_by_pid(payment_id)
        if result is None:
            return {}
        return result.decision

    def get_by_payment_id(self, payment_id):
        # Busco registro en Accertify
        accertify = RiskDataAccertify.find_by_pid(payment_id)
        result = (
            accertify
            if accertify is not None
            else RiskDataCybersource.find_by_pid(payment_id)
        )

        return result
