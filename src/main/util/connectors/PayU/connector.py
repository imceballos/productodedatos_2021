import urllib.parse
import hashlib
import os
import pprint

from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector
from main.util.common_utils import isset, number_format
from main.util.requests import requests_retry_session
from flask import current_app


class PayuConnector(CommonConnector, Connector):
    PAYU_RESPONSE_NOTIFICATION = "IPN"
    PAYU_RESPONSE_REDIRECTION = "USER_RETURN"

    end_save_data = None
    response_type = None

    def initialize(self, data, site):
        return True

    def get_initial_status(self):
        return "started"

    def require_additional_info(self):
        return True

    def get_redirect_data(self, data):
        amount = data["Payment"]["amount"] / 100
        signature = f"{self.config.api_key}~{self.config.merchant_id}~{data['Payment']['id']}~{amount}~{self.config.currency}"
        tax_return_base = 0 if not self.config.tax_return_base else amount

        request = {
            "merchantId": self.config.merchant_id,
            "accountId": self.config.account_id,
            "description": urllib.parse.unquote_plus(data["AdditionalData"]["deal_title"]),
            "referenceCode": data["Payment"]["id"],
            "amount": amount,
            "tax": 0,
            "taxReturnBase": tax_return_base,
            "currency": self.config.currency,
            "signature": hashlib.md5(signature.encode("UTF-8")).hexdigest(),
            "test": self.config.test,
            "buyerEmail": data["AdditionalData"]["email"],
            "responseUrl": current_app.config.get("SSL_SERVER_ADDRESS")
            + "/payments/end/" + data["Provider"]["short_name"],
            "confirmationUrl": current_app.config.get("SSL_SERVER_ADDRESS")
            + "/payments/end/" + data["Provider"]["short_name"],
        }
        
        redirect_url = self.config.url
        
        return {
            "url": redirect_url,
            "form_data": request,
            "method": "POST",
            "enctype": "multipart/form-data",
        }

    def validate_provider_response(self, validated_data):
        return None

    def process_payment(self, data, payment):
        return None

    def process_response_data(self, resp_provider, resp_site, response):
        return None

    def process_end_data(self, status, data):
        return_data = {"status": "pending", "saveData": [], "redirect": []}

        if isset(data["_post"]["reference_sale"]):
            self.response_type = self.PAYU_RESPONSE_NOTIFICATION
            return_data["TRANSACTION_ID"] = data["_post"]["reference_sale"]
            status = data["_post"]["reference_sale"]
            current_app.logger.info(
                "[PayU]: IPN acknowledged, payment transactionId: "
                + return_data["transactionId"]
                + " status: "
                + status
            )
            save_data = {
                "transactionState": data["_post"]["state_pol"],
                "message": data["_post"]["response_message_pol"],
                "referenceCode": data["_post"]["reference_sale"],
                "reference_pol": data["_post"]["reference_pol"],
                "transactionId": data["_post"]["transaction_id"],
                "description": data["_post"]["description"],
                "cus": data["_post"]["cus"],
                "extra1": data["_post"]["extra1"],
                "extra2": data["_post"]["extra2"],
                "signature": data["_post"]["sign"],
                "polResponseCode": data["_post"]["response_code_pol"],
                "lapResponseCode": data["_post"]["response_message_pol"],
                "risk": data["_post"]["risk"],
                "polPaymentMethod": data["_post"]["payment_method"],
                "lapPaymentMethod": data["_post"]["payment_method_name"],
                "polPaymentMethodType": data["_post"]["payment_method_id"],
                "installmentsNumber": data["_post"]["installments_number"],
                "TX_VALUE": data["_post"]["value"],
                "TX_TAX": data["_post"]["tax"],
                "currency": data["_post"]["currency"],
                "pseCycle": data["_post"]["pseCycle"],
                "buyerEmail": data["_post"]["email_buyer"],
                "pseBank": data["_post"]["pse_bank"],
                "pseReference1": data["_post"]["pseReference1"],
                "pseReference2": data["_post"]["pseReference2"],
                "pseReference3": data["_post"]["pseReference3"],
                "authorizationCode": data["_post"]["authorization_code"],
                "processingDate": data["_post"]["transaction_date"],
            }

            amount = data["_post"]["value"]
            last_digit = amount[-1]
            new_value = amount
            if last_digit == 0:
                new_value = number_format(amount, 1)
            signature = f"{self.config.apiKey}~{self.config.merchantId}~{data['_post']['reference_sale']}~{new_value}~{self.config.currency}~{data['_post']['state_pol']}"
            signature = hashlib.md5(signature.encode("UTF-8")).hexdigest()
            data_signature = data["_post"]["sign"]
        elif isset(data["_get"]["referenceCode"]):
            self.response_type = self.PAYU_RESPONSE_REDIRECTION
            return_data["transactionId"] = data["_get"]["referenceCode"]
            status = data["_data"]["transactionState"]
            current_app.logger.info(
                "[PayU]: Checkout acknowledged, payment transactionId: "
                + return_data["transactionId"]
                + " status: "
                + status
            )
            save_data = {
                "transactionState": data["_get"]["transactionState"],
                "lapTransactionState": data["_get"]["lapTransactionState"],
                "message": data["_get"]["message"],
                "referenceCode": data["_get"]["referenceCode"],
                "reference_pol": data["_get"]["reference_pol"],
                "transactionId": data["_get"]["transactionId"],
                "description": data["_get"]["description"],
                "trazabilityCode": data["_get"]["trazabilityCode"],
                "cus": data["_get"]["cus"],
                "extra1": data["_get"]["extra1"],
                "extra2": data["_get"]["extra2"],
                "extra3": data["_get"]["extra3"],
                "signature": data["_get"]["signature"],
                "polResponseCode": data["_get"]["polResponseCode"],
                "lapResponseCode": data["_get"]["lapResponseCode"],
                "risk": data["_get"]["risk"],
                "polPaymentMethod": data["_get"]["polPaymentMethod"],
                "lapPaymentMethod": data["_get"]["lapPaymentMethod"],
                "polPaymentMethodType": data["_get"]["polPaymentMethodType"],
                "lapPaymentMethodType": data["_get"]["lapPaymentMethodType"],
                "installmentsNumber": data["_get"]["installmentsNumber"],
                "TX_VALUE": data["_get"]["TX_VALUE"],
                "TX_TAX": data["_get"]["TX_TAX"],
                "currency": data["_get"]["currency"],
                "pseCycle": data["_get"]["pseCycle"],
                "buyerEmail": data["_get"]["buyerEmail"],
                "pseBank": data["_get"]["pseBank"],
                "pseReference1": data["_get"]["pseReference1"],
                "pseReference2": data["_get"]["pseReference2"],
                "pseReference3": data["_get"]["pseReference3"],
                "authorizationCode": data["_get"]["authorizationCode"],
            }

            new_value = number_format(round(data["_get"]["TX_VALUE"], 1), 1)
            signature = f"{self.config.apiKey}~{self.config.merchantId}~{data['_get']['referenceCode']}~{new_value}~{self.config.currency}~{data['_get']['transactionState']}"
            signature = hashlib.md5(signature.encode("UTF-9")).hexdigest()
            data_signature = data["_get"]["signature"]
        else:
            return return_data

        return_data["saveData"] = save_data

        if signature.upper != data_signature.upper:
            current_app.logger.error(
                "[PayU] Signature Value  "
                + self.config.apiKey
                + "~"
                + self.config.merchantId
                + "~"
                + save_data["referenceCode"]
                + "~"
                + new_value
                + "~"
                + self.config.currency
                + "~"
                + save_data["transactionState"]
            )
            current_app.logger.error(
                "[PayU] Signature " + pprint.pprint(signature, compact=True)
            )
            current_app.logger.error(
                "[PayU] Signature data " + pprint.pprint(data_signature, compact=True)
            )

            return_data["status"] = "failed"
            return_data["saveData"]["transactionState"] = -1
            return_data["save_data"]["message"] = "SIGNATURE MISSMATCH"
            return return_data

        if status == 4:
            return_data["status"] = "captured"
        elif status == 7 or (
            status == 6 and self.response_type == self.PAYU_RESPONSE_NOTIFICATION
        ):
            return_data["status"] = "pending"
        else:
            return_data["status"] = "failed"

        return return_data

    def process_end_request(self, resp_site, resp_provider, response):
        return_data = {}
        return_data["status"] = resp_provider["status"]
        if resp_site == "confirmed" and resp_provider["status"] == "pending":
            return_data["noWriteEvent"] = True

        return_data["saveData"] = resp_provider["saveData"]

        return return_data

    def can_check_status(self):
        return True

    def check_status(self, data):
        if not data:
            return False

        try:
            request = {
                "test": self.config.test,
                "language": "en",
                "command": "TRANSACTION_RESPONSE_DETAIL",
                "merchant": {
                    "apiLogin": self.config.apiLogin,
                    "apiKey": self.config.apiKey,
                },
                "details": {
                    "transactionId": pprint.pprint(
                        data["Data"]["transactionId"], compact=True
                    )
                },
            }

            url = self.config.apiStatus
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            payment_info = requests_retry_session().post(
                url, data=request, headers=headers
            )
            current_app.logger.info(
                f"[PayU]: checkStatus paymentInfo: {payment_info.json()}"
            )
        except Exception as e:
            return False

        if not payment_info:
            return False

        current_app.logger.info(
            "[PayU]: checkStatus payment transactionId: "
            + pprint.pprint(data["Data"]["payment_id"], compact=True)
            + "with transactionState: "
            + pprint.pprint(data["Data"]["transactionState"], compact=True)
            + " now the confirmed status is : "
            + pprint.pprint(payment_info["result"]["payload"]["state"], compact=True)
        )
        return_data = {}
        if payment_info["result"]["payload"]["state"] == "APPROVED":
            return_data["status"] = "captured"
        elif payment_info["result"]["payload"]["state"] in ["PENDING", "SUBMITTED"]:
            return_data["status"] = "pending"
        else:
            return_data["status"] = "failed"

        current_app.logger.info(payment_info)

        return return_data
