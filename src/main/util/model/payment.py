"""Business logic for /payment model."""

import hashlib
import random
import random
from datetime import datetime

import dateutil.parser
from flask import current_app
from main import db
from main.models.payments_db import (
    Payment,
    Provider,
    Currency,
    Site,
    AdditionalDatum,
    RiskDataAccertify,
)
from main.util.app_controller import AppController
from main.util.common_utils import paranoid, convertRowProxy, datetime_to_str
from main.util.model.site import SiteControl


class PaymentControl(AppController):
    # Env vars
    payment_ttl = 100
    payment_ttl_from = 0
    payment_ttl_to = 100
    pre_salt = ""
    post_salt = ""
    CODE_PAY_PY_COUNTRY_MISSING = ""

    def __init__(self):
        AppController.__init__(self)
        self.transitionMatrix = {
            "NEW": {
                "-": {
                    "started": "IN_PROCESS",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                },
                "confirmed": {
                    "started": "IN_PROCESS",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                    "retained": "RETAINED",
                },
                "failed": {
                    "started": "IN_PROCESS",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                },
            },
            "IN_PROCESS": {
                "-": {
                    "failed": "FAILED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                },
                "confirmed": {
                    "confirmation_required": "CONFIRMED",
                    "captured": "FUNDS_CAPTURED",
                    "cancelled": "CANCELLED",
                    "failed": "FAILED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                    "refunded": "REFUNDED",
                    "retained": "RETAINED",
                },
                "failed": {
                    "-": "FAILED",
                    "started": "FAILED",
                    "confirmation_required": "FAILED",
                    "captured": "FAILED",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                },
            },
            "CONFIRMED": {
                "-": {
                    "failed": "FAILED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                },
                "confirmed": {
                    "captured": "FUNDS_CAPTURED",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                    "retained": "RETAINED",
                },
                "failed": {
                    "confirmation_required": "FAILED",
                    "failed": "FAILED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                },
            },
            "FUNDS_CAPTURED": {
                "confirmed": {
                    "refunded": "REFUNDED",
                },
            },
            "FAILED": {
                "confirmed": {
                    "captured": "FUNDS_CAPTURED",
                    "cancelled": "CANCELLED",
                },
            },
            "CANCELLED": {
                "confirmed": {
                    "captured": "FUNDS_CAPTURED",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                    "retained": "RETAINED",
                },
                "failed": {
                    "confirmation_required": "FAILED",
                    "failed": "FAILED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                },
            },
            "IN_REFUND": {},
            "REFUNDED": {},
            "EXPIRED": {},
            "REJECTED": {},
            "RETAINED": {
                "confirmed": {
                    "captured": "FUNDS_CAPTURED",
                    "failed": "FAILED",
                    "cancelled": "CANCELLED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                    "retained": "RETAINED",
                },
                "failed": {
                    "confirmation_required": "FAILED",
                    "failed": "FAILED",
                    "rejected": "REJECTED",
                    "pending": "IN_PROCESS",
                },
            },
        }

        self.canExpire = {
            "NEW",
            "IN_PROCESS",
        }

        self.siteResponses = {
            "-",
            "confirmed",
            "failed",
        }

        self.providerResponses = {
            "-",
            "started",
            "confirmation_required",
            "captured",
            "failed",
            "cancelled",
            "rejected",
            "pending",
            "refunded",
            "retained",
        }

    def update_payment_status(self, payment, response_vector):
        default_vector = {"site": "-", "provider": "-"}

        response_vector = {**default_vector, **response_vector}

        if isinstance(payment, int):
            payment = Payment().find_by_id(payment)
            print(payment.id)
            if not payment.id:
                current_app.logger.info("Can't transition a nonexistent payment.")
                return False

        payment_status = payment.status
        order_number = payment.order_number
        site_response = response_vector["site"]
        provider_response = response_vector["provider"]

        if site_response not in self.siteResponses:
            current_app.logger.info(f"Received invalid site response: {site_response}.")
            return False

        if provider_response not in self.providerResponses:
            current_app.logger.info(
                f"Received invalid provider response: {provider_response}."
            )
            return False

        current_app.logger.info(
            f"Trying to change payment status (order_number: {order_number}). [{payment_status}] ({site_response})({provider_response})"
        )

        if not self.transitionMatrix[payment_status][site_response][provider_response]:
            current_app.logger.info(
                f"Invalid transition for payment ID {payment['Payment']['id']}: [{payment_status}] ({site_response})({provider_response})"
            )
            return False

        payment.status = self.transitionMatrix[payment_status][site_response][
            provider_response
        ]
        save_payment = payment.save()

        if not save_payment:
            current_app.logger.info(
                "Error saving new status {} for payment {}".format(
                    payment.status, payment.id
                )
            )

        current_app.logger.info(
            "Payment status transition (order_number: {}): [{}] ({})({}) -> [{}]".format(
                order_number,
                payment_status,
                site_response,
                provider_response,
                payment.status,
            )
        )

        return payment.status

    def get_provider_data(self, provider, conditions):
        if conditions is None:
            return False

        if provider.isnumeric():
            provider = Provider.get_connector_id_by_id(provider)

        if "mercadopago" in provider:
            provider = "mercadopago"

        table_name = f"data_{provider}"
        sql_condition = ""

        for condition in conditions:
            if sql_condition != "":
                sql_condition += " AND "

            sql_condition += f"`{condition}` = '{conditions[condition]}'"

        query = f"SELECT * FROM `{table_name}` WHERE {sql_condition}"

        extra_data = db.session.execute(query)
        response = convertRowProxy(extra_data)

        if response is None or response == {}:
            return dict()

        return response

    def save_provider_data(self, payment_id, data, provider="", prefix=""):
        if data is None or not isinstance(data, dict):
            return False

        ignore_fields = ["_get", "_post"]

        if provider != "":
            provider = provider
        else:
            payment = Payment().find_by_id(payment_id)
            provider_associated = Provider.get_by_id(payment.provider_id)
            provider = provider_associated.connector_id

        if "mercadopago" in provider:
            provider = "mercadopago"

        table_name = "data_"

        if prefix != "":
            table_name = prefix + "_" + table_name

        table_name += provider.lower()

        payment_field = f"`payment_id` = '{payment_id}', "
        fields = ""
        insert = False

        for element in data:
            field = paranoid(element, ["_", "-", "*"])
            value = paranoid(data[element], ["_", "-", " ", ".", "@", ":", "/"])

            if field in ignore_fields:
                continue

            field = field.replace("-", "_")
            fields += f"`{field}` = '{value}', "

            insert = True

        if not insert:
            return True

        try:
            query = f"INSERT INTO `{table_name}` SET {payment_field} {fields} created = NOW(),modified = NOW() ON DUPLICATE KEY UPDATE {fields} modified = NOW()"
            db.session.execute(query)
            db.session.commit()
        except:
            current_app.logger.info(
                "Error trying to save_provider_data {} for payment {} with query {}".format(data, payment_id, query)
            )
            return False
        return True

    def find_to_validate(self, payment_id):
        payment = Payment().find_by_id(payment_id).__dict__
        currency = Currency().find_by_id(payment["currency_id"]).__dict__
        connector_id = Provider().get_connector_id_by_id(payment["provider_id"])
        response = {"Validate": {}}
        if payment is not None:
            response["Validate"]["payment_id"] = payment["id"]
            response["Validate"]["order_number"] = payment["order_number"]
            response["Validate"]["confirmation_code"] = payment["confirmation_code"]
            response["Validate"]["hash"] = payment["hash"]
            response["Validate"]["created"] = str(payment["created"])
            response["Validate"]["amount"] = payment["amount"]
            response["Validate"]["currency"] = currency["code"]
            response["Validate"]["connector_id"] = connector_id
            response["Validate"]["site_id"] = payment["site_id"]

        return response

    def expire(self, payment):
        if type(payment).__name__ == "int" or type(payment).__name__ == "float":
            payment = Payment().find_by_id(payment).__dict__

        if payment is None:
            current_app.logger.info("Trying to expire an empty payment" + payment)
            return False

        if payment["status"] not in self.canExpire:
            current_app.logger.info(
                "Can't expire a payment with status " + payment["status"]
            )
            return False

        mercadopago_offline_providers = ["mercadopago"]

        provider = Provider().get_by_id(payment["provider_id"])
        if provider["connector_id"] in mercadopago_offline_providers:
            provider_data = self.get_provider_data(
                provider["connector_id"], {"payment_id": payment["id"]}
            )
            if provider_data["payment_type"] != "ticket":
                current_app.logger.info(
                    "Only can expire offline methods from " + provider["short_name"]
                )
                return False

        d1 = dateutil.parser.parse(payment["created"])
        d2 = dateutil.parser.parse(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        diff = ((d2 - d1).seconds) / 60

        if diff < self.payment_ttl:
            current_app.logger.info(
                "Can't expire a payment created less than "
                + self.payment_ttl
                + " minutes ago"
            )
            return False

        payment_item = Payment.query.filter_by(id=payment["id"]).first()
        data = {"status": "EXPIRED"}

        try:
            payment_item.update(data)
        except:
            current_app.logger.info(
                "Error saving new status {} for payment {}".format(
                    data["status"], payment["id"]
                )
            )
            return False

        # Notificar a API
        site_response = SiteControl().hook_notify(payment, "failed", True)

        # Notificar a MP
        if provider["connector_id"] in mercadopago_offline_providers:
            connector = AppController.load_connector(provider["id"])
            cancel_payment = connector.cancel_payment(payment, provider_data)

            # Rollback status
            if not cancel_payment:
                payment_item = Payment.query.filter_by(id=payment["id"]).first()
                data = {"status": "IN_PROCESS"}

                try:
                    payment_item.update(data)
                except:
                    current_app.logger.info(
                        "Error saving new status {} for payment {}".format(
                            data["status"], payment["id"]
                        )
                    )
                    return False

                return False

        current_app.logger.info(
            f"Payment {payment['id']} expired. Previous status '{payment['status']}'"
        )

        return True

    def expire_payments(self, provider=""):
        conditions = [
            "created <= NOW() - INTERVAL " + self.payment_ttl_from + " HOUR",
            "created >= NOW() - INTERVAL " + self.payment_ttl_from + " HOUR",
            "status IN (" + ",".join(self.canExpire) + ")",
        ]
        # Si viene el provider se debe agregar a las condiciones
        if provider != "":
            # Si provider está separado por comas se debe manejar como array
            if "," in provider:
                provider = provider.split(",")

            if type(provider).__name__ == "str":
                providers = Provider.get(provider)
            else:
                providers = Provider.get_all(provider)
                providers = [prov.__dict__ for prov in providers]

            if providers is not None or len(providers) > 0:
                conditions.append(
                    "provider_id IN (" + ",".join(providers.keys()) + ")",
                )

        # Execute Query
        table_name = f"payments"
        sql_condition = ""

        for condition in conditions:
            if sql_condition != "":
                sql_condition += " AND "

            sql_condition += f"`{condition}` = '{conditions[condition]}'"

        query = f"SELECT * FROM `{table_name}` WHERE {sql_condition}"
        payments = db.session.execute(query)
        payments = convertRowProxy(payments)

        if payments is None or payments == {}:
            return False

        result = {"success": 0, "error": 0}

        for payment in payments:
            if self.expire(payment):
                result["success"] = result["success"] + 1
            else:
                result["error"] = result["error"] + 1

        return result

    def get_for_site(self, site_id, order_number):
        if type(site_id).__name__ != "int" and type(site_id).__name__ != "float":
            return {}

        payments = Payment.find_all_by_siteid_order(site_id, order_number)
        return [payment.__dict__ for payment in payments]

    def get_refund_data(self, provider, conditions):
        if type(conditions).__name__ != "dict":
            return False

        if type(provider).__name__ == "int" or type(provider).__name__ == "float":
            provider = Provider.get_connector_id_by_id(provider)

        # Execute Query
        table_name = f"refund_data_{provider}"
        sql_condition = ""

        for condition in conditions:
            if sql_condition != "":
                sql_condition += " AND "

            sql_condition += f"`{condition}` = '{conditions[condition]}'"

        if conditions != {}:
            query = f"SELECT * FROM `{table_name}` WHERE {sql_condition}"
        else:
            query = f"SELECT * FROM `{table_name}`"

        payments = db.session.execute(query)
        payments = convertRowProxy(payments)

        if payments is None or payments == {}:
            return dict()

        return payments

    def get_site_id(self, payment_id):
        if type(payment_id).__name__ != "int" and type(payment_id).__name__ != "float":
            current_app.logger.info("Payment is not numeric")
            return False

        return Payment.query.filter_by(id=payment_id).value("site_id")

    def get_transition_matrix(self):
        return self.transitionMatrix

    def update_status_details(self, payment_id, detail):
        payment = Payment.query.filter_by(id=payment_id).first()
        data = {"status_details": detail}

        if payment is None:
            current_app.logger.info("Payment not found: " + str(payment_id))
            return False

        try:
            payment.update(data)
        except:
            current_app.logger.info(
                "Error saving new status {} for payment {}".format(detail, payment_id)
            )
            return False

        return True

    def get_valid_site_responses(self):
        return self.siteResponses

    def get_valid_provider_responses(self):
        return self.providerResponses

    def generate_confirmation_code(
            self, payment_id, only_return=False, confirmation_code=False
    ):
        payment = Payment.query.filter_by(id=payment_id).first()
        if confirmation_code is not False:
            code = confirmation_code
        else:
            if payment.confirmation_code is not None:
                code = payment.confirmation_code
                only_return = True
            else:
                code = random.randint(1000000, 9999999)

        if only_return is False:
            data = {"confirmation_code": code}
            try:
                payment.update(data)
            except:
                current_app.logger.info(
                    "Error saving confirmation code {} for payment {}".format(
                        code, payment_id
                    )
                )
                return False

        return code

    def get_provider_extra_data(self, provider, conditions):
        if type(conditions).__name__ != "dict":
            return False

        if type(provider).__name__ == "int":
            provider = Provider.get_connector_id_by_id(provider)

        # Execute Query
        table_name = f"extra_data_{provider}"
        sql_condition = ""

        for condition in conditions:
            if sql_condition != "":
                sql_condition += " AND "

            sql_condition += f"`{condition}` = '{conditions[condition]}'"

        if conditions != {}:
            query = f"SELECT * FROM `{table_name}` WHERE {sql_condition}"
        else:
            query = f"SELECT * FROM `{table_name}`"

        extra_data = db.session.execute(query)
        extra_data = convertRowProxy(extra_data)
        extra_data = datetime_to_str(extra_data)

        if extra_data is None or extra_data == {}:
            return dict()

        return extra_data

    def save_additional_data(self, payment_id, data, prefix=""):
        if type(payment_id).__name__ != "int" and type(payment_id).__name__ != "float":
            current_app.logger.info("Payment id is not numeric")
            return False

        if data is None or data is {}:
            current_app.logger.info("Empty data")
            return False

        insert_data = ""

        for element in data:
            if element is None or data[element] is None:
                current_app.logger.info(f"{element} is None or empty")
            if element in ["numero", "number", "cvc"]:
                data[element] = "****"
            insert_data += f"({payment_id}, '{prefix}{element}', '{data[element]}'),"

        insert_data = insert_data[0:-1]

        query = f"INSERT IGNORE INTO additional_data (`payment_id`, `key`, `value`) VALUES {insert_data}"
        current_app.logger.info(f"Executing query {query}")
        db.session.execute(query)
        db.session.commit()

        return True

    def update_provider_extra_data(self, provider, key, data):
        if key is None or data is None:
            current_app.logger.info("Key or data is none")
            return False

        if type(provider).__name__ == "int":
            provider = Provider.get_connector_id_by_id(provider)

        table_name = f"extra_data_{provider}"
        sql_key = ""

        for column in key:
            if sql_key != "":
                sql_key += ", "

            sql_key += f"`{column}` = '{key[column]}'"

        sql_data = ""

        for column in data:
            if sql_data != "":
                sql_data += ", "

            sql_data += f"`{column}` = '{data[column]}'"

        query = f"INSERT INTO `{table_name}` SET {sql_key}, {sql_data}, created = NOW(), modified = NOW() ON DUPLICATE KEY UPDATE {sql_data}, modified = NOW()"

        current_app.logger.info(f"Executing query {query}")
        db.session.execute(query)
        db.session.commit()

        return True

    def calculateHash(self, payment):
        if (
                "site_id" in payment
                and payment["site_id"] is not None
                and "provider_id" in payment
                and payment["provider_id"] is not None
                and "order_number" in payment
                and payment["order_number"] is not None
                and "amount" in payment
                and payment["amount"] is not None
        ):
            pre_hash = (
                    self.pre_salt
                    + str(payment["site_id"])
                    + str(payment["provider_id"])
                    + str(payment["order_number"])
                    + str(payment["amount"])
                    + self.post_salt
            )

            hash = hashlib.sha512(str(pre_hash).encode("utf-8"))

            return hash.hexdigest()

        return ""

    def verifyHash(self, payment):
        if payment is None:
            current_app.logger.info("Payment not found")
            return False

        if "hash" not in payment or payment["hash"] is None:
            current_app.logger.info("Payment have not hash")
            return False

        hash = self.calculateHash(payment)

        return hash == payment["hash"]

    def get_payment_data(self, type_id, request_id, site_id=""):
        if type_id == "payment_id":
            payments = [Payment.find_by_id(request_id)]
        elif type_id == "order_number":
            if site_id == "":
                payments = Payment.find_by_order_number(request_id)
            else:
                site = Site.get_by_id(site_id)
                if site is None:
                    return {
                        "error": "Need a valid site id",
                        "error_code": self.CODE_PAY_PY_COUNTRY_MISSING,
                        "status": False
                    }
                payments = Payment.find_all_by_siteid_order(site_id, request_id)
        else:
            response = {
                "error": "type_id",
                "error_description": "Type_id only can be order_number or payment_id",
            }
            current_app.logger.info(response)
            response['status'] = False
            return response

        if payments is None or len(payments) == 0 or payments[0] is None:
            response = {
                "error": "invalid_id",
                "error_description": f"{type_id} not found",
            }
            current_app.logger.info(response)
            response['status'] = False
            return response
        else:
            result = []
            for payment in payments:
                response = {
                    "Payment": {},
                    "Site": {},
                    "Provider": {},
                    "Currency": {},
                    "AdditionalData": [],
                    "ProviderPaymentData": {},
                    "RiskData": {},
                }
                site = Site.get_by_id(payment.site_id)
                provider = Provider.get_by_id(payment.provider_id)
                currency = Currency.find_by_id(payment.currency_id)
                additional_data = AdditionalDatum.get_by_payment_id(payment.id)
                response["Payment"]["id"] = payment.id
                response["Payment"]["order_number"] = payment.order_number
                response["Payment"]["amount"] = payment.amount
                response["Payment"]["status"] = payment.status
                response["Payment"]["confirmation_code"] = payment.confirmation_code
                response["Payment"]["ip"] = payment.ip
                response["Payment"]["created"] = str(payment.created)
                response["Payment"]["modified"] = str(payment.modified)
                if site is not None:
                    response["Site"]["id"] = site.id
                    response["Site"]["name"] = site.name
                    response["Site"]["display_name"] = site.display_name
                if provider is not None:
                    response["Provider"]["name"] = provider.name
                    response["Provider"]["short_name"] = provider.short_name
                    response["Provider"]["alias"] = provider.alias
                if currency is not None:
                    response["Currency"]["name"] = currency.name
                    response["Currency"]["code"] = currency.code
                    response["Currency"]["conversion"] = currency.conversion
                    response["Currency"]["template"] = currency.template
                    response["Currency"]["referral_value"] = currency.referral_value
                    response["Currency"]["min_payment"] = currency.min_payment
                    response["Currency"]["decimals_sep"] = currency.decimals_sep
                    response["Currency"]["thousands_sep"] = currency.thousands_sep
                    response["Currency"]["decimals"] = currency.decimals

                additional_data_cleaned = []
                if additional_data is not None and additional_data != []:
                    for data in additional_data:
                        cleaned = data.__dict__
                        del cleaned["_sa_instance_state"]
                        additional_data_cleaned.append(cleaned)
                response["AdditionalData"] = additional_data_cleaned

                if provider is not None:
                    table_name = "data_" + provider.connector_id.lower()
                    query = f"SELECT * FROM `{table_name}` WHERE `payment_id` = '{payment.id}'"
                    data_provider = db.session.execute(query)
                    data_provider = convertRowProxy(data_provider, "list")

                    if data_provider != [] and data_provider is not None:
                        response["ProviderPaymentData"] = datetime_to_str(
                            data_provider, "list"
                        )
                risk_data = RiskDataAccertify.find_by_pid(payment.id)

                if risk_data is not None:
                    risk_data = risk_data.__dict__
                    del risk_data["_sa_instance_state"]
                    response["RiskData"] = datetime_to_str(risk_data)

                result.append(response)

        return result
