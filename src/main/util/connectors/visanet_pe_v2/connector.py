import locale

from flask import current_app
from main.util.connectors.visanet_pe.plugin import VisaNetPe
from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector
from main.util.model.payment import PaymentControl
from main.models.models import Payment


class Visanet_peConnector(Connector, CommonConnector):

    # Const Vars
    SERVER_NAME = ""
    SERVER_PORT = ""

    # Plugin config vars
    additional_data = {}
    config = {}

    data = None
    site = None

    # def __init__(self, data, site):
        

    def get_initial_status(self):
        return "started"

    def need_redirect(self):
        return True

    def need_specific_data(self):
        return False

    def can_check_status(self):
        return True
    
    def initialize(self, data, site):
        self.data = data
        self.site = site
        return True
        
    def get_redirect_data(self, data):
        server_name = self.SERVER_NAME
        server_port = self.SERVER_NAME
        redirect_data = {}
        redirect_data["url"] = False
        
        url = "https://" + server_name
        internal_redirect_url = (
            url
            + f"/payments/end/{data['Provider']['short_name']}?request={data['Payment']['id']}"
        )

        plugin = VisaNetPe(self.config)
        tx_session = plugin.generate_session(data, self.additional_data)

        if tx_session is not None:
            visa_data = {
                "session": tx_session,
                "merchant": self.config.MERCHANT_ID,
                "amount": round(data["Payment"]["amount"] / 100, 2),
                "payment_id": data["Payment"]["id"],
                "render": "visanet",
                "component": self.config.URL_JS,
                "callbackUrl": internal_redirect_url,
                "description": self.additional_data["description"]
                if (
                    self.additional_data is not None
                    and "description" in self.additional_data
                    and self.additional_data["description"] is not None
                )
                else "",
            }
            redirect_data = {
                "url": '', #  TODO: esto es mal, este conector deberia hacer un redir interno...self.config.formulario_pago,
                "method": "POST",
                "enctype": "application/x-www-form-urlencoded",
                "form_data": visa_data,
            }
        else:
            current_app.logger.info(
                f"[VisanetRest] Failed to get TxSession at getRedirectData: {data['payment']['id']}"
            )

        return redirect_data

    def process_end_data(self, status, data):
        if (
            "_post" in data
            and "transaction_token" in data["_post"]
            and data["_post"]["transaction_token"] is not None
        ) and (
            "_get" in data
            and "request" in data["_get"]
            and data["_get"]["request"] is not None
        ):
            plugin = VisaNetPe(self.config)
            transaction_token = data["_post"]["transaction_token"]
            transaction_id = data["_get"]["request"]
            if transaction_token is None or transaction_id is None:
                current_app.logger.info(
                    f"[VisanetRest] Failed to get required params at processEndData:: transactionToken: {transaction_token} - transactionId {transaction_id}"
                )
                return {"status": "failed"}

            payment = Payment.query.filter_by(id=transaction_id)

            if (
                "payment" in payment
                and "id" in payment["id"]
                and payment["payment"]["id"] is not None
            ):
                amount = round(payment["payment"]["amount"] / 100, 2)
                data_auth_visanet = plugin.generate_authorization(
                    amount, transaction_id, transaction_token
                )
                if data_auth_visanet is not None:
                    if (
                        (
                            "data_map" in data_auth_visanet
                            and data_auth_visanet["data_map"] is not None
                        )
                        or (
                            "data" in data_auth_visanet
                            and data_auth_visanet["data"] is not None
                        )
                    ) and data_auth_visanet["error_code"] == 400:
                        data_auth_visanet["data_map"] = (
                            data_auth_visanet["data_map"]
                            if (
                                "data_map" in data_auth_visanet
                                and data_auth_visanet["data_map"] is not None
                            )
                            else data_auth_visanet["data"]
                        )
                        save_data = self.set_save_data(data_auth_visanet)
                        if data_auth_visanet["data_map"]["ACTION_CODE"] == 000:
                            current_app.logger.info(
                                f"[VisanetRest] Authorized by provider at processEndData: {transaction_id}"
                            )
                            return {
                                "transaction_id": transaction_id,
                                "status": "captured",
                                "save_data": "",
                            }
                        else:
                            current_app.logger.info(
                                f"[VisanetRest] NO Authorized by provider at processEndData: {transaction_id}"
                            )
                            return {
                                "transaction_id": transaction_id,
                                "status": "failed",
                                "save_data": "",
                            }
                    else:
                        current_app.logger.info(
                            f"[VisanetRest] GenerateAuthorization DataMap was empty at processEndData: {transaction_id}"
                        )
                        return {
                            "transaction_id": transaction_id,
                            "status": "failed",
                            "save_data": "",
                        }
                else:
                    current_app.logger.info(
                        f"[VisanetRest] GenerateAuthorization was empty at processEndData: {transaction_id}"
                    )
                    return {
                        "transaction_id": transaction_id,
                        "status": "failed",
                        "save_data": "",
                    }

        else:
            transaction_id = (
                data["_get"]["request"]
                if "_get" in data
                and "request" in data["_get"]
                and data["_get"]["request"] is not None
                else ""
            )
            current_app.logger.info(
                "[VisanetRest] Failed to get essential params at processEndData"
            )
            return {
                "transaction_id": transaction_id,
                "status": "failed",
                "save_data": "",
            }

    def process_end_response(self, resp_site, resp_provider, response):
        if resp_site == "confirmed" and resp_provider["status"] == "captured":
            return {"status": "captured", "save_data": resp_provider["save_data"]}
        else:
            return {"status": "failed", "save_data": resp_provider["save_data"]}

    def check_status(self, data):
        payment = Payment()
        if data is None:
            return {"status": False, "desc": "no Data provided"}
        conditions = {"payment_id": data["payment"]["id"]}
        provider_data = PaymentControl().get_provider_data(
            data["provider"]["id"], conditions
        )

        if (
            "transaction_id" in provider_data
            and provider_data["transaction_id"] is not None
        ):
            plugin = VisaNetPe(self.config)
            data_auth_visanet = plugin.retrieve_transaction(
                provider_data["transaction_id"]
            )
            if data_auth_visanet is not None:
                if (
                    "data_map" in data_auth_visanet
                    and data_auth_visanet["data_map"] is not None
                ):
                    save_data = self.set_save_data(data_auth_visanet)
                    if data_auth_visanet["data_map"]["ACTION_CODE"] == 000:
                        response = {
                            "transaction_id": data["payment"]["id"],
                            "save_data": save_data,
                            "status": "captured",
                        }
                        current_app.logger.info(
                            "[VisanetRestPe] response was Authorized for PaymentID"
                        )
                    else:
                        response = {
                            "transaction_id": data["payment"]["id"],
                            "save_data": save_data,
                            "status": "failed",
                        }
                        current_app.logger.info(
                            "[VisanetRestPe] response was not Authorized for PaymentID"
                        )
                    if response["status"] in ["captured", "pending"]:
                        site_response = "confirmed"
                    else:
                        site_response = "failed"
                    final_provider_response = self.process_end_response(
                        site_response, response, ""
                    )
                    final_provider_response["site_response"] = site_response
                    return final_provider_response
                else:
                    response = {"status": "failed"}
                    current_app.logger.info(
                        "[VisanetRestPE] No dataMap available for PaymentID"
                    )
            else:
                response = {"status": "failed"}
                current_app.logger.info(
                    "[VisanetRestPE] response was empty for PaymentID"
                )
        else:
            current_app.logger.info("[VisanetRestPE] Not found PaymentID")
            return {
                "status": False,
                "desc": "This transaction was aborted by user or miserably losted by provider",
            }

    def set_save_data(self, data_auth_visanet):
        if data_auth_visanet != None or type(data_auth_visanet).__name__ != "list":
            current_app.logger.info(
                "[VisanetRestPe] Provider parameter is empty or is not an object"
            )
            return False

        save_data = {
            save_data["ecore_transaction_uuid"]: data_auth_visanet["header"][
                "ecore_transaction_uuid"
            ]
            if (
                "header" in data_auth_visanet
                and "ecore_transaction_uuid" in data_auth_visanet["header"]
                and None != data_auth_visanet["header"]["ecore_transaction_uuid"]
            )
            else "",
            save_data["ecore_transaction_date"]: data_auth_visanet["header"][
                "ecore_transaction_date"
            ]
            if (
                "header" in data_auth_visanet
                and "header" in data_auth_visanet["header"]
                and None != data_auth_visanet["header"]["ecore_transaction_date"]
            )
            else "",
            save_data["millis"]: data_auth_visanet["header"]["millis"]
            if (
                "header" in data_auth_visanet
                and "header" in data_auth_visanet["header"]
                and None != data_auth_visanet["header"]["millis"]
            )
            else "",
            save_data["order_token_id"]: data_auth_visanet["order"]["tokenId"]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["token_id"]
            )
            else "",
            save_data["installment"]: data_auth_visanet["order"]["installment"]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["installment"]
            )
            else "",
            save_data["currency"]: data_auth_visanet["order"]["currency"]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["currency"]
            )
            else "",
            save_data["authorized_amount"]: data_auth_visanet["order"][
                "authorized_amount"
            ]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["authorized_amount"]
            )
            else "",
            save_data["authorization_code"]: data_auth_visanet["order"][
                "authorization_code"
            ]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["authorization_code"]
            )
            else "",
            save_data["action_code"]: data_auth_visanet["order"]["action_code"]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["action_code"]
            )
            else "",
            save_data["trace_number"]: data_auth_visanet["order"]["trace_number"]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["trace_number"]
            )
            else "",
            save_data["transaction_date"]: data_auth_visanet["order"][
                "transaction_date"
            ]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["transaction_date"]
            )
            else "",
            save_data["transaction_id"]: data_auth_visanet["order"]["transaction_id"]
            if (
                "order" in data_auth_visanet
                and "order" in data_auth_visanet["order"]
                and None != data_auth_visanet["order"]["transaction_id"]
            )
            else "",
            save_data["datamap_currency"]: data_auth_visanet["dataMap"]["CURRENCY"]
            if (
                "data_map" in data_auth_visanet
                and "CURRENCY" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["CURRENCY"]
            )
            else "",
            save_data["datamap_terminal"]: data_auth_visanet["dataMap"]["TERMINAL"]
            if (
                "data_map" in data_auth_visanet
                and "TERMINAL" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["TERMINAL"]
            )
            else "",
            save_data["datamap_transaction_date"]: data_auth_visanet["dataMap"][
                "TRANSACTION_DATE"
            ]
            if (
                "data_map" in data_auth_visanet
                and "TRANSACTION_DATE" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["TRANSACTION_DATE"]
            )
            else "",
            save_data["datamap_action_code"]: data_auth_visanet["dataMap"][
                "ACTION_CODE"
            ]
            if (
                "data_map" in data_auth_visanet
                and "ACTION_CODE" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["ACTION_CODE"]
            )
            else "",
            save_data["datamap_trace_number"]: data_auth_visanet["dataMap"][
                "TRACE_NUMBER"
            ]
            if (
                "data_map" in data_auth_visanet
                and "TRACE_NUMBER" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["TRACE_NUMBER"]
            )
            else "",
            save_data["datamap_eci_description"]: data_auth_visanet["dataMap"][
                "ECI_DESCRIPTION"
            ]
            if (
                "data_map" in data_auth_visanet
                and "ECI_DESCRIPTION" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["ECI_DESCRIPTION"]
            )
            else "",
            save_data["datamap_eci"]: data_auth_visanet["dataMap"]["ECI"]
            if (
                "data_map" in data_auth_visanet
                and "ECI" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["ECI"]
            )
            else "",
            save_data["datamap_signature"]: data_auth_visanet["dataMap"]["SIGNATURE"]
            if (
                "data_map" in data_auth_visanet
                and "SIGNATURE" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["SIGNATURE"]
            )
            else "",
            save_data["datamap_card"]: data_auth_visanet["dataMap"]["CARD"]
            if (
                "data_map" in data_auth_visanet
                and "CARD" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["CARD"]
            )
            else "",
            save_data["datamap_merchant"]: data_auth_visanet["dataMap"]["MERCHANT"]
            if (
                "data_map" in data_auth_visanet
                and "MERCHANT" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["MERCHANT"]
            )
            else "",
            save_data["datamap_brand"]: data_auth_visanet["dataMap"]["BRAND"]
            if (
                "data_map" in data_auth_visanet
                and "BRAND" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["BRAND"]
            )
            else "",
            save_data["datamap_status"]: data_auth_visanet["dataMap"]["STATUS"]
            if (
                "data_map" in data_auth_visanet
                and "STATUS" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["STATUS"]
            )
            else "",
            save_data["datamap_action_description"]: data_auth_visanet["dataMap"][
                "ACTION_DESCRIPTION"
            ]
            if (
                "data_map" in data_auth_visanet
                and "ACTION_DESCRIPTION" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["ACTION_DESCRIPTION"]
            )
            else "",
            save_data["datamap_adquirente"]: data_auth_visanet["dataMap"]["ADQUIRENTE"]
            if (
                "data_map" in data_auth_visanet
                and "ADQUIRENTE" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["ADQUIRENTE"]
            )
            else "",
            save_data["datamap_id_unico"]: data_auth_visanet["dataMap"]["ID_UNICO"]
            if (
                "data_map" in data_auth_visanet
                and "ID_UNICO" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["ID_UNICO"]
            )
            else "",
            save_data["datamap_amount"]: data_auth_visanet["dataMap"]["AMOUNT"]
            if (
                "data_map" in data_auth_visanet
                and "AMOUNT" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["AMOUNT"]
            )
            else "",
            save_data["datamap_process_code"]: data_auth_visanet["dataMap"][
                "PROCESS_CODE"
            ]
            if (
                "data_map" in data_auth_visanet
                and "PROCESS_CODE" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["PROCESS_CODE"]
            )
            else "",
            save_data["datamap_transaction_id"]: data_auth_visanet["dataMap"][
                "TRANSACTION_ID"
            ]
            if (
                "data_map" in data_auth_visanet
                and "TRANSACTION_ID" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["TRANSACTION_ID"]
            )
            else "",
            save_data["datamap_authorization_code"]: data_auth_visanet["dataMap"][
                "AUTHORIZATION_CODE"
            ]
            if (
                "data_map" in data_auth_visanet
                and "AUTHORIZATION_CODE" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["AUTHORIZATION_CODE"]
            )
            else "",
            save_data["datamap_quota_deferred"]: data_auth_visanet["dataMap"][
                "QUOTA_DEFERRED"
            ]
            if (
                "data_map" in data_auth_visanet
                and "QUOTA_DEFERRED" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["QUOTA_DEFERRED"]
            )
            else "",
            save_data["datamap_quota_ni_discount"]: data_auth_visanet["dataMap"][
                "QUOTA_NI_DISCOUNT"
            ]
            if (
                "data_map" in data_auth_visanet
                and "QUOTA_NI_DISCOUNT" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["QUOTA_NI_DISCOUNT"]
            )
            else "",
            save_data["datamap_quota_number"]: data_auth_visanet["dataMap"][
                "QUOTA_NUMBER"
            ]
            if (
                "data_map" in data_auth_visanet
                and "QUOTA_NUMBER" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["QUOTA_NUMBER"]
            )
            else "",
            save_data["datamap_quota_ni_amount"]: data_auth_visanet["dataMap"][
                "QUOTA_NI_AMOUNT"
            ]
            if (
                "data_map" in data_auth_visanet
                and "QUOTA_NI_AMOUNT" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["QUOTA_NI_AMOUNT"]
            )
            else "",
            save_data["datamap_quota_amount"]: data_auth_visanet["dataMap"][
                "QUOTA_AMOUNT"
            ]
            if (
                "data_map" in data_auth_visanet
                and "QUOTA_AMOUNT" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["QUOTA_AMOUNT"]
            )
            else "",
            save_data["datamap_settlement_status"]: data_auth_visanet["dataMap"][
                "SETTLEMENT"
            ]
            if (
                "data_map" in data_auth_visanet
                and "SETTLEMENT" in data_auth_visanet["data_map"]
                and None != data_auth_visanet["data_map"]["SETTLEMENT"]
            )
            else "",
        }
        return save_data

    def require_additional_info(self):
        pass

    def validate_provider_response(self, data, validate_data):
        pass

    def process_payment(self, data, payment):
        pass

    def process_response_data(self, resp_provider, resp_site, response):
        pass