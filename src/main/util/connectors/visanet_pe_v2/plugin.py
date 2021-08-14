import base64
import requests
import json
from flask import current_app


class VisaNetPe:

    config = {}

    def __init__(self, config_data):
        self.config = config_data

    def set_config(self, config_data):
        self.config = config_data

    def get_config(self):
        return self.config

    def generate_token(self):
        access_data = requests.post(
            self.config.URL_SECURITY,
            data={},
            auth=(self.config.USER, self.config.PWD),
        )

        if access_data.status_code != 201:
            print(
                f"[VisanetRest] Failed to create Token at generateToken status code was :: {access_data['status']}"
            )
            return False

        return access_data.text

    def generate_session(self, data, additional_data):
        token = self.generate_token()
        
        session = {
            "amount": round(data["Payment"]["amount"] / 100, 2),
            "antifraud": {
                "clientIp": data["Payment"]["ip"]
                if (
                    "payment" in data
                    and "id" in data["Payment"]
                    and data["Payment"]["id"] is not None
                )
                else "",
                "merchantDefineData": {
                    "MDD1": self.config.MERCHANT_ID,
                    "MDD3": "WEB",
                    "MDD4": additional_data["email"]
                    if (
                        "email" in additional_data
                        and additional_data["email"] is not None
                    )
                    else "",
                },
                "MDD21": additional_data["frequent_user"]
                if (
                    "frequent_user" in additional_data
                    and additional_data["frequent_user"] is not None
                )
                else "",
                "MDD77": additional_data["days_of_life"]
                if (
                    "days_of_life" in additional_data
                    and additional_data["days_of_life"] is not None
                )
                else 1,
            },
            "channel": "WEB",
            "recurrenceMaxAmount": None,
        }

        response = requests.post(
            self.config.URL_SESSION + self.config.MERCHANT_ID,
            data=session,
            headers={
                "Authorization": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        if response is not None and response.status_code == 200:
            return response["response"]["session_key"]
        else:
            return False

    def generate_authorization(self, amount, purchase_number, transaction_token):
        token = self.generate_token()
        data = {
            "antifraud": None,
            "captureType": "manual",
            "channel": "web",
            "countable": True,
            "order": {
                "amount": amount,
                "currency": self.config.currency,
                "purchaseNumber": purchase_number,
                "tokenId": transaction_token,
            },
            "recurrence": None,
            "sponsored": None,
        }

        response = requests.post(
            self.config.URL_AUTHORIZATION + self.config.MERCHANT_ID,
            data=data,
            headers={
                "Authorization": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        if response is not None and response["status"] in [200, 201, 400]:
            return response["response"]
        else:
            return False

    def retrieve_transaction(self, transaction_id, query_type="transaction"):
        token = self.generate_token()
        response = requests.get(
            self.config.URL_CONSULTA
            + query_type
            + "/"
            + self.config.MERCHANT_ID
            + "/"
            + transaction_id,
            headers={"Authorization": token, "Accept": "application/json"},
        )
        if response is not None and response["status"] in [200, 201, 400]:
            return response["response"]
        else:
            return False