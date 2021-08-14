import requests
import json


class MP:

    access_token = None
    client_id = None
    client_secret = None
    sandbox = False

    def __init__(self, client_id="", client_secret=""):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(
            f"https://api.mercadopago.com/oauth/token",
            data=data,
        )
        return response.json()["access_token"]

    def sandbox_mode(self, enable=None):
        if enable != None:
            self.sandbox = True
        return self.sandbox

    ### Get information for specific payment
    def get_payment(self, payment_id):
        access_token = self.get_access_token()
        preferences = dict()
        url_prefix = "/sandbox" if self.sandbox else ""
        response = requests.get(
            f"https://api.mercadopago.com{url_prefix}/v1/payments/{payment_id}?access_token={access_token}"
        )
        
        preferences["status"] = response.status_code
        preferences["response"] = response.json()
        return preferences

    def get_payment_info(self, payment_id):
        return self.get_payment(payment_id)

    ### Get information for specific authorized payment
    def get_authorized_payment(self, payment_id):
        access_token = self.get_access_token()
        response = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}?access_token={access_token}&status=authorized"
        )
        return response.json()

    ### Refund accredited payment
    def refund_payment(self, collection_id, data):
        access_token = self.get_access_token()
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"https://api.mercadopago.com/v1/payments/{collection_id}/refunds?access_token={access_token}",
            data=json.dumps(data),
            headers=headers,
        )
        return response.json()

    ### Cancel pending payment
    def cancel_payment(self, payment_id):
        access_token = self.get_access_token()
        headers = {"Content-Type": "application/json"}
        data = {"status": "cancelled"}
        response = requests.put(
            f"https://api.mercadopago.com/v1/payments/{payment_id}?access_token={access_token}",
            data=json.dumps(data),
            headers=headers,
        )
        return response.json()

    ### Search payments according to filters, with pagination
    def search_payment(self, filters, offset=0, limit=0):
        access_token = self.get_access_token()

        filters["offset"] = offset
        filters["limit"] = limit

        url_prefix = "/sandbox" if self.sandbox else ""

        filter_url = ""
        for key, value in filters.items():
            filter_url += f"&{key}={value}"

        response = requests.get(
            f"https://api.mercadopago.com{url_prefix}/v1/payments/search?access_token={access_token}{filter_url}"
        )
        return response.json()

    ### Create a checkout preference
    def create_preference(self, preference):
        access_token = self.get_access_token()
        preferences = dict()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
        response = requests.post(
            f"https://api.mercadopago.com/checkout/preferences",
            data=json.dumps(preference),
            headers=headers,
        )
        preferences["status"] = response.status_code
        preferences["response"] = response.json()
        return preferences

    ### Update a checkout preference
    def update_preference(self, preference_id, preference):
        access_token = self.get_access_token()
        headers = {"Content-Type": "application/json"}
        response = requests.put(
            f"https://api.mercadopago.com/checkout/preferences/{preference_id}?access_token={access_token}",
            data=json.dumps(preference),
            headers=headers,
        )
        return response.json()

    ### Get a checkout preference
    def get_preference(self, preference_id):
        access_token = self.get_access_token()
        response = requests.get(
            f"https://api.mercadopago.com/checkout/preferences/{preference_id}?access_token={access_token}"
        )
        return response.json()

    ### Get card token
    ### card params
    ### cardNumber, email, cardholder {'name': ''}, expirationYear, expirationMonth, securityCode
    def get_card_token(self, card):
        access_token = self.get_access_token()
        response = requests.put(
            f"https://api.mercadopago.com/v1/card_tokens?access_token={access_token}",
            data=card,
        )
        return response["id"]

    ### Create a preapproval payment
    def create_preapproval_payment(self, preapproval_payment):
        # TODO: preapproval endpoint not found
        pass

    ### Get a preapproval payment
    def get_preapproval_payment(self, preapproval_payment_id):
        # TODO: preapproval endpoint not found
        pass

    ### Update a preapproval payment
    def update_preapproval_payment(self, preapproval_payment_id):
        # TODO: preapproval endpoint not found
        pass

    ### Cancel a preapproval payment
    def cancel_preapproval_payment(self, preapproval_payment_id):
        # TODO: preapproval endpoint not found
        pass