import base64
from datetime import datetime

import requests, json
from flask import current_app, session

from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector


class PaypalConnector(Connector, CommonConnector):
    url_pay = None
    client_id = None
    secret_id = None

    def initialize(self, data: dict, site: str) -> bool:
        self.url_pay    = self.config.URL_PAYPAL
        self.client_id  = self.config.PAYPAL_CLIENT_ID
        self.secret_id  = self.config.PAYPAL_SECRET_ID
        
        response = self.created_token_paypal()
        
        if type(response) is bool:
            current_app.logger.info(
                    f"[Paypal] Failed to initialize due token hasn't been generated"
                )
            return False

        session['access_token'] = response['access_token']

        pay_order = {
            "intent": "CAPTURE",
            'purchase_units': []
        }
        payment_amount = {
            "currency_code": data['currency'],
            "value": data['amount']
        }
        pay_order['purchase_units'].append({'amount': payment_amount})

        headers = {
                    "Content-Type": "application/json", 
                    "Authorization": f"Bearer {response['access_token']}"
                }

        url_order_created = f"{self.url_pay}v2/checkout/orders"

        response = requests.request("POST", url_order_created, headers=headers, data=json.dumps(pay_order))
        response = json.loads(response.text)

        if 'status' in response and response['status'] == 'CREATED':
            session['payments'] = response
            session['payments_id'] = response['id']
            return True
        
        current_app.logger.info(
                    f"[Paypal] Failed to create payment request. Error: {response}"
                )
        return False

    def created_token_paypal(self):
        url = f"{self.url_pay}v1/oauth2/token"

        payload = 'grant_type=client_credentials'

        message = f"{self.client_id}:{self.secret_id}"
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        secret_base64_pp = base64_bytes.decode('ascii')

        headers = {
            'Authorization': f"Basic {secret_base64_pp}",
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            paypal_token_response = json.loads(response.text)

            if 'access_token' in paypal_token_response:
                return paypal_token_response
            else:
                current_app.logger.info(
                    f"[Paypal] Failed to create token for checkout. Error: {response.status_code}"
                )
                return False
        except Exception as exc:
            current_app.logger.info(
                f"[Paypal] Failed to create token for checkout. Error: {exc}"
            )
            return False

    def get_initial_status(self) -> str:
        return 'started'

    def require_additional_info(self) -> bool:
        return True

    def need_redirect(self) -> bool:
        return True

    def get_redirect_data(self, data: dict) -> dict:
        pay_response = session['payments']

        redirect = {
            'url': '',
            'method': 'GET',
            'enctype': 'application/json',
        }
        if pay_response['status'] == 'CREATED':
            for link in pay_response['links']:
                if link['rel'] == 'approve':
                    redirect['url'] = link['href']
        if pay_response['status'] == 'COMPLETED':
            for link in pay_response['purchase_units'][0]['payments']['authorizations'][0]['links']:
                if link['rel'] == 'capture':
                    redirect['url'] = link['href']
                    redirect['method'] = 'POST'
        return redirect

    def validate_provider_response(self, data: dict, validate_data: dict) -> dict:
        # TODO
        pass

    def process_payment(self, data: dict, payment) -> dict:
        # TODO
        pass

    def process_response_data(self, resp_provider, resp_site, response):
        # TODO
        pass

    def process_end_data(self, status: str, data: dict):
        if 'payment' in session and 'data' in session['payments']:
            payment_data = session['payments']['data']
            session.pop('payments')
        else:
            return {
                'status': 'failed'
            }

        if 'access_token' in session:
            token = session['access_token']
            session.pop('access_token')
        else:
            return {
                'status': 'failed'
            }

        if 'token' not in data['_get']:
            return {
                'status': 'failed'
            }
        if token != data['_get']['token']:
            return {
                'status': 'failed'
            }

        payment_order_capture = self.finalize(payment_data, token)

        if type(payment_order_capture) is bool:
            return {
                'status': 'failed'
            }

        if 'status' in payment_order_capture:
            return {
                'transaction_id': payment_data['id'],
                'status': 'captured',
                'save_data': payment_order_capture
            }
        else:
            return {
                'transaction_id': payment_data['id'],
                'status': 'failed',
                'save_data': payment_order_capture
            }

    def process_end_response(self, resp_site: str, resp_provider: dict, response):

        if 'confirmed' in resp_site:
            return {
                'status': 'captured',
                'save_data': resp_provider['save_data']
            }
        else:
            return {
                'status': 'failed',
                'save_data': resp_provider['save_data']
            }

    def finalize(self, payment_data: dict, token: str):
        payment_amount = payment_data['purchase_units']['amount']['value']
        payment_currency = payment_data['purchase_units']['amount']['currency_code']

        url_order_capture = f"{self.url_pay}v2/checkout/orders/{payment_data['id']}/capture"
        headers = {'Content-Type: application/json', f"Authorization: Bearer {token}"}

        try:
            response = requests.post(url_order_capture, header=headers)

            if 'status' in response:
                return response
            else:
                now = datetime.now()
                return {
                    'TOKEN': token,
                    'TIMESTAMP': datetime.timestamp(now),
                    'CORRELATIONID': response['debug_id'],
                    'ACK': 'Failed',
                    'VERSION': 'v2',
                    'BUILD': '?',
                    'TRANSACTIONID': '',
                    'TRANSACTIONTYPE': '',
                    'PAYMENTTYPE': '',
                    'ORDERTIME': '',
                    'AMT': payment_amount,
                    'FEEAMT': '',
                    'TAXAMT': '',
                    'CURRENCYCODE': payment_currency,
                    'PAYMENTSTATUS': '',
                    'PENDINGREASON': '',
                    'REASONCODE': '',
                }
        except Exception as exc:
            print(exc)
            return False
