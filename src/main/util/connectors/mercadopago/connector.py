from flask import current_app
from datetime import datetime
import pytz
import locale
import json

from main.util.connectors.mercadopago.plugin import MP
from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector


class MercadopagoConnector(Connector, CommonConnector):

    # Const Vars
    MERCADOPAGO_RESPONSE_NOTIFICATION = "IPN"
    MERCADOPAGO_RESPONSE_REDIRECTION = "USER_RETURN"

    # Connector vars
    mercado_pago = None
    response_type = None
    payment_response = None
    confirmation_data = None

    # TODO
    # This vars need to be env variable (In PHP $this->Config->read('variable'))
    site_id = 0
    SERVER_NAME = ""
    SERVER_PORT = ""
    binary = ""

    def initialize(self, data, site):
        self.mercado_pago = self.create_mp()
        return True if self.mercado_pago is not None else False
	
    def create_mp(self):
        mercado_pago = MP(self.config.client_id, self.config.client_secret)
        mercado_pago.sandbox = self.config.sandbox_mode
        return mercado_pago

    def get_initial_status(self):
        return "started"

    def require_additional_info(self):
        return True

    def need_redirect(self):
        return True

    def has_refund(self):
        return True

    def get_redirect_data(self, data):
        server_name = self.SERVER_NAME
        server_port = self.SERVER_PORT
        url = "https://" + server_name

        self.success_URL = url + self.config.success_url
        self.failure_URL = url + self.config.error_url
        binary_mode = False

        if self.config.currency_code == "COP":
            binary_date = self.config.binary
            tz = pytz.timezone("America/Bogota")
            hora_CO = datetime.now(tz)
            hora_CO_start = pytz.utc.localize(
                binary_date["start"], is_dst=None
            ).astimezone(tz)
            hora_CO_end = pytz.utc.localize(binary_date["end"], is_dst=None).astimezone(
                tz
            )
            if hora_CO >= hora_CO_start and hora_CO <= hora_CO_end:
                binary_mode = True

        # Get additional data out of preference_data dict to clean code
        if (
            "getaways_category" in data["AdditionalData"]
            and data["AdditionalData"]["getaways_category"] != None
        ):
            travel_category = data["AdditionalData"]["getaways_category"]
        else:
            travel_category = ""

        if (
            "category_id" in data["AdditionalData"]
            and data["AdditionalData"]["category_id"] != None
        ):
            category_id = data["AdditionalData"]["category_id"]
        else:
            category_id = "coupons"

        if (
            "phone_number" in data["AdditionalData"]
            and data["AdditionalData"]["phone_number"] != None
        ):
            phone_number = data["AdditionalData"]["phone_number"]
        else:
            phone_number = ""

        if (
            "first_name" in data["AdditionalData"]["user"]
            and data["AdditionalData"]["user"]["first_name"] != None
        ):
            first_name = data["AdditionalData"]["user"]["first_name"]
        else:
            first_name = ""

        if (
            "last_name" in data["AdditionalData"]["user"]
            and data["AdditionalData"]["user"]["last_name"] != None
        ):
            last_name = data["AdditionalData"]["user"]["last_name"]
        else:
            last_name = ""

        preference_data = {
            "items": [{
                "title": data["AdditionalData"]["descripcion"],
                "quantity": 1,
                "currency_id": self.config.currency_code,
                "unit_price": float(
                    locale.format_string(
                        "%.*f", (2, data["AdditionalData"]["amount"] / 100), True
                    )
                ),
                "category_id": category_id,
                "travel_category": travel_category,
            }],
            "payer": {
                "phone": {"area_code": "", "number": phone_number},
                "email": data["AdditionalData"]["emailComprador"],
                "name": first_name,
                "surname": last_name,
            },
            "back_urls": {
                "success": self.success_URL,
                "failure": self.failure_URL,
                "pending": "",
            },
            "auto_return": "approved",
            "binary_mode": binary_mode,
            "payment_methods": {
                "excluded_payment_methods": self.config.excluded_payment_methods,
                "excluded_payment_types": self.config.excluded_payment_types,
                "installments": self.config.maximum_installments,
                "default_installments": self.config.default_installments,
            },
            "external_reference": data["AdditionalData"]["transactionId"],
        }

        redirect_data = {
            "method": "GET",
            "enctype": "application/x-www-form-urlencoded",
            "form_data": {"pref_id": ""},
        }

        try:
            preference = self.mercado_pago.create_preference(preference_data)
        except Exception as e:
            current_app.logger.info(
                f"[Mercadopago] Failed to create preference for checkout. Error: {e}"
            )
            redirect_data["url"] = False

        if (
            "status" in preference
            and preference["status"] == 201
            and "id" in preference["response"]
        ):
            if self.config.sandbox_mode:
                redirect_data["url"] = preference["response"]["sandbox_init_point"]
            else:
                redirect_data["url"] = preference["response"]["init_point"]

            redirect_data["form_data"]["pref_id"] = preference["response"]["id"]

            redirect_data["save_data"] = {
                "collector_id": preference["response"]["collector_id"],
                "operation_type": preference["response"]["operation_type"],
                "payer_email": preference["response"]["payer"]["email"],
                "client_id": preference["response"]["client_id"],
                "preference_external_reference": preference["response"][
                    "external_reference"
                ],
                "preference_date_created": preference["response"]["date_created"],
                "preference_id": preference["response"]["id"],
            }
        else:
            current_app.logger.info(
                "[Mercadopago] Invalid response from MP: Check preferences"
            )
            redirect_data["url"] = False

        return redirect_data

    def get_payment_id(self, data):
        if "id" not in data or "topic" not in data or data["topic"] != "payment":
            current_app.logger.info(
                "[Mercadopago] Invalid data from MP at confirmation"
            )
            return False

        if self.mercado_pago == None:
            self.create_mp()

        if self.mercado_pago == False:
            return False

        payment_info = self.get_payment_info(data["id"])

        if "status" not in payment_info or payment_info["status"] != 200:
            current_app.logger.info("[Mercadopago] Wrong status received from MP.")
            return False

        if "response" not in payment_info and "external_reference" not in payment_info:
            current_app.logger.info(
                "[Mercadopago] Missign external reference (payment id)."
            )
            return False

        self.confirmation_data = payment_info

        return self.confirmation_data["external_reference"]

    def validate_provider_response(self, data, validate_data):
        result = {"status": "failed"}

        if "status" in self.confirmation_data:
            if self.confirmation_data["status"] == "approved":
                result["status"] = "captured"
            # TBI: pending, in_process, rejected, refunded, cancelled, in_mediation

        return result

    def process_payment(self, data, payment):
        # Not used
        pass

    def process_response_data(self, resp_provider, resp_site, response):
        if (
            "status" in self.confirmation_data
            and self.confirmation_data["status"] == "approved"
        ):
            return {"payment_captured": True}

    def process_end_data(self, status, data):
        # Payment is considered a failure until verified
        payment_info = {}
        result = {"status": "pending"}
        
        if self.mercado_pago == None:
            self.mercado_pago = self.create_mp()

        if self.mercado_pago == False:
            return result

        # If this is an async notification by MercadoPago
        if status == "nostatus" and "topic" in data and data["topic"] == "payment":
            self.response_type = self.MERCADOPAGO_RESPONSE_NOTIFICATION
            if "id" in data:
                payment_info = self.mercado_pago.get_payment_info(data["id"])
                
            if "status" in payment_info and payment_info["status"] == 200:
                result["transaction_id"] = payment_info['response']["external_reference"]
                if payment_info['response']["payment_type_id"] == "credit_card":
                    result["installments"] = payment_info['response']["installments"]
                self.payment_response = payment_info

                if payment_info['response']["status"] == "approved":
                    result["status"] = "captured"
                    current_app.logger.info(
                        "[Mercadopago]: Notification acknowledged, successful payment transactionId: "
                        + result["transaction_id"]
                    )
                elif (
                    "in_process" in payment_info['response']["status"]
                    and "pending" in payment_info['response']["status"]
                ):
                    result["status"] = "pending"
                    current_app.logger.info(
                        "[Mercadopago]: Notification acknowledged, payment pending transactionId: "
                        + result["transaction_id"]
                    )
                elif "cancelled" in payment_info['response']["status"]:
                    result["status"] = "cancelled"
                elif "refunded" in payment_info['response']["status"]:
                    result["status"] = "refunded"
                else:
                    result["status"] = "failed"
            else:
                return False

        # If this is the user coming back from the checkout
        elif "collection_id" in data and data["collection_id"] is not None:
            self.response_type = self.MERCADOPAGO_RESPONSE_REDIRECTION
            valid_payment = False
            
            transaction_id = data["external_reference"]

            if transaction_id is not None:
                result["transaction_id"] = transaction_id
                if data["collection_id"] is not None:
                    payment_info = self.mercado_pago.get_payment_info(data["collection_id"])
                    
                    if "status" in payment_info and payment_info["status"] == 200:
                        if "response" in payment_info and payment_info["response"] is not None:
                            result["transaction_id"] = payment_info["response"]["external_reference"]
                            if payment_info["response"]["payment_type_id"] == "credit_card":
                                result["installments"] = payment_info["response"]["installments"]

                            self.payment_response = payment_info
                            if payment_info["response"]["status"] in [
                                "approved",
                                "pending",
                                "in_process",
                            ]:
                                current_app.logger.info(
                                    "[Mercadopago]: Checkout acknowledged, payment transactionId: "
                                    + result["transaction_id"]
                                    + " status: "
                                    + payment_info["response"]["status"]
                                )
                                valid_payment = True
                                mp_status = payment_info["response"]["status"]

                                # Validacion de estado devuelto en GET contra resultado busqueda
                            if (
                                "collection_status" in data
                                and payment_info["response"]["status"]
                                != data["collection_status"]
                            ):
                                current_app.logger.info(
                                    "[Mercadopago]: Error distinct status GET and return get_payment_info. paymentInfo "
                                )
                        else:
                            current_app.logger.info(
                                "[Mercadopago] payment not found id "
                                + transaction_id
                                + " status "
                                + status
                                + " paymentInfo"
                            )
                    else:
                        current_app.logger.info(
                            "[Mercadopago] Error calling get_payment_info status"
                        )
                elif status == "success":
                    current_app.logger.info("[Mercadopago] collection_id null")
            else:
                current_app.logger.info(
                    "[Mercadopago] transaction id not found" + status
                )
            if status == "success" and valid_payment:
                if mp_status in ["pending", "in_process"]:
                    result["status"] = "pending"
                    current_app.logger.info(
                        "[Mercadopago]: User returned, pending payment transactionId: "
                        + transaction_id
                    )
                else:
                    result["status"] = "captured"
                    current_app.logger.info(
                        "[Mercadopago]: User returned, successful payment transactionId: "
                        + transaction_id
                    )
            elif status == "pending" and valid_payment:
                result["status"] = "pending"
                current_app.logger.info(
                    "[Mercadopago]: User returned, pending payment transactionId: "
                    + transaction_id
                )
            elif status == "failure":
                result["status"] = "failed"
                current_app.logger.info(
                    "[Mercadopago]: User returned, unfinished payment transactionId: "
                    + transaction_id
                )

        return result

    def process_end_response(self, resp_site, resp_provider, response):
        result = {"status": "pending"}
       
        if self.response_type == self.MERCADOPAGO_RESPONSE_NOTIFICATION:
            result["status_code"] = 200
            result["body"] = ""
            result["response"] = "do_not_autorender"

        if resp_site == "confirmed" and resp_provider["status"] == "captured":
            result["status"] = "captured"
        elif resp_site == "confirmed" and resp_provider["status"] == "pending":
            result["status"] = "pending"
        elif resp_site == "failed" and resp_provider["status"] == "failed":
            result["status"] = "failed"
        elif resp_site == "failed" and resp_provider["status"] == "refunded":
            result["status"] = "refunded"
        elif resp_site == "failed" and resp_provider["status"] == "cancelled":
            result["status"] = "cancelled"

        if self.payment_response != None:
            result["save_data"] = {
                "collection_id": self.payment_response["response"]["id"],
                "site_id": response['site_id'],
                "collection_date_created": self.payment_response["response"]["date_created"],
                "collection_date_approved": self.payment_response["response"]["date_approved"],
                "money_release_date": self.payment_response["response"]["money_release_date"],
                "order_id": self.payment_response["response"]["order"]["id"],
                "transaction_amount": self.payment_response["response"]["transaction_amount"],
                "currency_id": self.payment_response["response"]["currency_id"],
                "status": self.payment_response["response"]["status"],
                "status_detail": self.payment_response["response"]["status_detail"],
                "payment_type": self.payment_response["response"]["payment_type_id"],
                "installments": self.payment_response["response"]["installments"],
            }

        return result

    def can_check_status(self):
        return True

    def need_specific_data(self):
        return False

    def check_status(self, data):
        if data == None:
            return False

        if self.mercado_pago == None:
            self.mercado_pago = self.create_mp()

        if self.mercado_pago == False:
            return False

        try:
            if "id" in data:
                payment_info = self.get_payment_info(data)
            elif "provider_data" in data and "collection_id" in data["provider_data"]:
                payment_info = self.get_payment_info_by_collection_id(
                    data["provider_data"]
                )
            else:
                current_app.logger.info(
                    "[Mercadopago] checkStatus Payment Id nor Collection ID were not settled"
                )
                return False
        except Exception as e:
            current_app.logger.info(
                f"[Mercadopago] checkStatus can't find external_reference. Error: {e}"
            )
            return False

        result = {}
        if payment_info["results"][0] == []:
            current_app.logger.info("Payment not found")
            return result

        if payment_info["results"][0]["status"] == "approved":
            result["status"] = "captured"
            result["site_response"] = "confirmed"
        elif (
            "in_process" in payment_info["results"][0]["status"]
            and "pending" in payment_info["results"][0]["status"]
        ):
            result["status"] = "pending"
            result["site_response"] = "confirmed"
        elif "cancelled" in payment_info["results"][0]["status"]:
            result["status"] = "cancelled"
            result["site_response"] = "failed"
        elif "refunded" in payment_info["results"][0]["status"]:
            result["status"] = "refunded"
            result["site_response"] = "confirmed"
        else:
            result["status"] = "failed"
            result["site_response"] = "failed"

        current_app.logger.info("[MercadoPago] paymentInfo in checkStatus")
        return result

    def get_payment_info(self, data):
        if data == None:
            return False

        if self.mercado_pago == None:
            self.mercado_pago = self.create_mp(data)

        if self.mercado_pago == False:
            return False

        try:
            filters = {"id": data["id"]}
            payment_info = self.mercado_pago.search_payment(filters, 0, 100)
            data_tx = payment_info

            if (
                "response" in payment_info
                and "results" in payment_info
                and len(payment_info["results"]) > 0
            ):
                for result in payment_info["results"]:
                    if result["status"] == "approved":
                        data_tx["response"]["results"] = result
                        break

            return data_tx
        except Exception as e:
            current_app.logger.info("[MercadoPago] Failed to getPaymentInfo")
            return False

    def get_payment_info_by_collection_id(self, data):
        if data == None:
            return False

        if self.mercado_pago == None:
            self.mercado_pago = self.create_mp(data)

        if self.mercado_pago == False:
            return False

        try:
            data_tx = self.mercado_pago.get_payment_info(data["collection_id"])
            payment_info = {"response": {"results": None}}
            payment_info["results"] = data_tx["response"]
        except Exception as e:
            current_app.logger.info(
                f"[MercadoPago] Failed to getPaymentInfoByCollectionID. Error: {e}"
            )
            return False

        return payment_info

    def cancel_payment(self, data, provider_data):
        if data == None:
            return False

        if self.mercado_pago == None:
            self.mercado_pago = self.create_mp(data)

        if self.mercado_pago == False:
            return False

        try:
            payment_info = self.mercado_pago.cancel_payment(
                provider_data["collection_id"]
            )
        except Exception as e:
            response = {}
            response["status"] = 4202
            response[
                "desc"
            ] = "[Mercadopago] Transaction must be cancelled and not refunded, but for some reason it fails"
            return response

        return payment_info

    def refund_payment(self, data, provider_data, amount=0):
        payment_info = {}

        if data["payment"]["payment"] == None:
            return False

        if self.mercado_pago == None:
            self.mercado_pago = self.create_mp()

        if self.mercado_pago == False:
            return False

        # Check if payment exists
        if "collection_id" in provider_data:
            try:
                search_payment = self.get_payment_info(data["payment"]["payment"])
                if (
                    search_payment["results"] != []
                    and data["payment"]["payment"]["id"]
                    == search_payment["results"][0]["id"]
                ):
                    provider_data["collection_id"] = search_payment["results"][0]["id"]
                else:
                    message = (
                        "[Mercadopago] Can't find Payment, it won't be possible to perform a refund: "
                        + data["payment"]["payment"]["id"]
                    )
                    current_app.logger.info(message)
                    response = {}
                    response["status"] = 3022
                    response["desc"] = message
                    return response
            except Exception as e:
                message = (
                    "[Mercadopago] Can't find Payment, it won't be possible to perform a refund: "
                    + data["payment"]["payment"]["id"]
                )
                current_app.logger.info(message)
                response = {}
                response["status"] = 3012
                response["desc"] = message
                return response
        else:
            current_app.logger.info("No Collection ID found")

        # Get Payment Info
        try:
            payment_info = self.mercado_pago.get_payment_info(
                provider_data["collection_id"]
            )
        except Exception as e:
            message = (
                "[Mercadopago] Cant get payment Info : "
                + data["payment"]["payment"]["id"]
            )
            current_app.logger.info(message)
            response = {}
            response["status"] = 3000
            response["desc"] = message
            return response

        # In process Payments must be cancelled
        if (
            payment_info["status"] == "pending"
            or payment_info["status"] == "in_process"
        ):
            message = (
                "[Mercadopago]: Attempting to cancel transaction: "
                + data["payment"]["payment"]["id"]
            )
            current_app.logger.info(message)

            cancel = self.cancel_payment(data, provider_data)
            if "status" in cancel and cancel["status"] == 4022:
                return cancel
            else:
                payment_info["prefix"] = ""
                payment_info["saveData"] = {
                    "collection_id": cancel["response"]["id"],
                    "status": cancel["response"]["status"],
                    "status_detail": cancel["response"]["status_detail"],
                }
                return payment_info

        # Refunds are only made for approved payments
        if payment_info["status"] != "approved":
            message = (
                "[Mercadopago]: Trying to refund a "
                + payment_info["status"]
                + " transaction: "
                + data["payment"]["payment"]["id"]
            )
            current_app.logger.info(message)
            response = {}
            response["status"] = 3001
            response["desc"] = message
            return response

        # Refunds are only made for payments less than 90 days
        now = datetime.now()
        approved_date = datetime.strptime(
            payment_info["date_approved"][0:19], "%Y-%m-%dT%H:%M:%S"
        )
        days_diff = (now - approved_date).days

        if days_diff > self.refund_limit_days:
            message = (
                "[Mercadopago] Payment too old ( >= 90 days) to be refunded. Approved: "
                + payment_info["date_approved"]
            )
            current_app.logger.info(message)
            response = {}
            response["status"] = 3002
            response["desc"] = message
            return response

        if "transaction_amount_refunded" in payment_info:
            pending_refund_amount = (
                payment_info["transaction_amount"]
                - payment_info["transaction_amount_refunded"]
            )
            if amount > pending_refund_amount:
                message = (
                    "[Mercadopago] Refund amount value "
                    + amount
                    + " exceed max. refound value of "
                    + pending_refund_amount
                    + " - Payment ID: "
                    + data["payment"]["payment"]["id"]
                )
                current_app.logger.info(message)
                response = {}
                response["status"] = 3003
                response["desc"] = message
                return response

        # No more than 20 refunds for Payment
        if "refunds" in payment_info and len(payment_info["refunds"]) >= 20:
            message = (
                "[Mercadopago] You've reached refunds limit (20) for this payment "
                + data["payment"]["payment"]["id"]
            )
            current_app.logger.info(message)
            response = {}
            response["status"] = 3010
            response["desc"] = message
            return response

        # Refund Payment
        refund_data = {}
        if amount > 0:
            refund_data["amount"] = amount
        try:
            # Refund total amount
            self.mercado_pago.refund_payment(
                provider_data["collection_id"], refund_data
            )
        except Exception as e:
            message = (
                "[Mercadopago]: An error has ocurred trying to refund Payment: "
                + data["payment"]["payment"]["id"]
            )
            current_app.logger.info(message)
            response = {}
            response["status"] = 3004
            response["desc"] = message
            return response

        # Get Payment Info to return with updated status
        if "status" in payment_info and payment_info["status"] == 201:
            payment_info["save_data"] = {
                "amount": payment_info["amount"],
                "date_created": payment_info["date_created"],
                "refund_id": payment_info["id"],
                "collection_id": payment_info["payment_id"],
                "source_id": payment_info["source"]["id"],
                "source_name": payment_info["source"]["name"],
                "source_type": payment_info["source"]["type"],
                "status": payment_info["status"],
            }
            payment_info["prefix"] = "refund"

        try:
            get_updated_payment_info = self.mercado_pago.get_payment_info(
                provider_data["collection_id"]
            )
            payment_info["save_data_2"] = {
                "status": get_updated_payment_info["status"],
                "status_detail": get_updated_payment_info["status_detail"],
            }
        except Exception as e:
            message = (
                "[Mercadopago]: Can't update Payment: "
                + data["payment"]["payment"]["id"]
            )

        return payment_info
