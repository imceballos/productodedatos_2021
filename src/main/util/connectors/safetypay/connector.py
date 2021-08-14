import hashlib
import json
from datetime import datetime

import requests
import xmltodict
from main.util.common_utils import isset

from src.main.models.payments_db import Payment
from src.main.util.connectors.common_connector import CommonConnector
from src.main.util.connectors.connector import Connector


class SafetyPayConnector(Connector, CommonConnector):
    created_express_token = 'AGREGAMOS AQUI LA URL'

    def initialize(self, data, site):
        return True

    def get_initial_status(self):
        return 'started'

    def require_additional_info(self):
        # TODO
        pass

    def need_redirect(self):
        return True

    def get_redirect_data(self, data):
        payload = {
            'ApiKey': self.config.apikey,
            'RequestDateTime': datetime.now().strftime('Y-m-d\TH:i:s'),
            'CurrencyCode': self.config.currencyCode,
            'Amount': data['Payment']['amount'] / 100,
            'MerchantSalesID': data['Payment']['id'],
            'Language': self.config.language,
            'TrackingCode': '',
            'ExpirationTime': self.config.expirationTime,
            'FilterBy': '',
            'TransactionOkURL': self.config.success_url,
            'TransactionErrorURL': self.config.error_url,
            'ResponseFormat': 'XML'
        }

        payload['Signature'] = self.get_signature(payload)
        url = self.config.createExpressToken
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, headers=headers, data=payload)
        response_json = json.dumps(xmltodict.parse(response.content, dict_constructor=dict), indent=4)
        response_json = json.loads(response_json)
        if 'CreateExpressTokenResponse' in response_json:
            return {
                'url': response_json['CreateExpressTokenResponse']['ExpressTokenResponse']['ShopperRedirectURL'],
                'method': 'POST',
                'enctype': 'application/x-www-form-urlencoded',
                'form_data': []
            }
        else:
            return {}

    def validate_provider_response(self, data, validate_data):
        if '_post' in data and 'MerchantReferenceNo' in data['_post']:
            return {
                'paymentId': data['_post']['MerchantReferenceNo'],
                'saveData': data['_post'],
                'status': 'captured'
            }
        else:
            return {
                'status': 'failed'
            }
        pass

    def process_payment(self, data, payments):
        # TODO
        pass

    def process_response_data(self, response_provider, response_side, response):
        if response_provider['status'] == 'capture' and response_side == 'confirmed':
            return True
        else:
            return False

    def process_end_data(self, status, data):
        payment_id = None
        save_data = {}
        if '_post' in data and 'MerchantSalesID' in data['post']:
            payment_id = data['_post']['MerchantSalesID']
        elif '_post' in data and 'MerchantReferenceNo' in data['post']:
            payment_id = data['_post']['MerchantSalesID']

        if payment_id:
            save_data['ApiKey'] = data['_post']['ApiKey'] if 'ApiKey' in data['_post'] else ''
            save_data['RequestDateTime'] = data['_post']['RequestDateTime'] if 'RequestDateTime' in data[
                '_post'] else ''
            save_data['MerchantSalesID'] = payment_id if payment_id else ''
            save_data['ReferenceNo'] = data['_post']['ReferenceNo'] if 'ReferenceNo' in data['_post'] else ''
            save_data['CreationDateTime'] = data['_post']['CreationDateTime'] if 'CreationDateTime' in data[
                '_post'] else ''
            save_data['Amount'] = data['_post']['Amount'] if 'Amount' in data['_post'] else ''
            save_data['CurrencyID'] = data['_post']['CurrencyID'] if 'CurrencyID' in data['_post'] else ''
            save_data['PaymentReferenceNo'] = data['_post']['PaymentReferenceNo'] if 'PaymentReferenceNo' in data[
                '_post'] else ''
            save_data['Status'] = data['_post']['Status'] if 'Status' in data['_post'] else ''
            save_data['Signature'] = data['_post']['Signature'] if 'Signature' in data['_post'] else ''

            return {
                'transaction_id': payment_id,
                'save_data': save_data,
                'status': 'capture'
            }
        else:
            return {
                'status': 'failed'
            }

    def process_end_response(self, response_provider, response_side, response):
        safety_pay_response = True
        pay = Payment()
        payment = pay.find_by_id(response_provider['transaction_id'])
        if payment['Payment']['status'] == 'FUNDS_CAPTURE':
            safety_pay_response = True
        if response_side == 'confirmed' and response_provider['status'] == 'capture':
            pay_data = response_provider['save_data']
            pay_data['ResponseDateTime'] = datetime.now().strftime("Y-m-d\TH:i:s")
            pay_data['OrderNo'] = pay_data['MerchantSalesID']
            pay_data['Signature'] = self.get_signature(pay_data)
            return {
                'status': 'capture',
                'dave_data': response_provider['save_data'],
                'response': safety_pay_response
            }
        else:
            return {
                'status': 'failed',
                'response': False
            }

    def get_payment_id(self, data):
        if '_post' in data:
            if 'MerchantReferenceNo' in data['_post']:
                return {
                    'payment_id': data['_post']['merchantReferenceNo']
                }
        else:
            return {
                'status': 'failed'
            }

    def get_signature(self, params):
        items_params = params.items()
        list_values = ['RequestDateTime', 'CurrencyCode', 'Amount', 'MerchantSalesID', 'Language', 'TrackingCode',
                       'ExpirationTime', 'TransactionOkURL', 'TransactionErrorURL']
        all_params_concatenate = ''
        if isset(params[0]):
            for elem, value in items_params:
                for elem_list in list_values:
                    if elem == elem_list:
                        items_params[elem] = (value.lstrip()).rstrip()
                        all_params_concatenate += items_params[elem]
        else:
            for elem, value in items_params:
                items_params[elem] = (value.lstrip()).rstrip()
                all_params_concatenate += items_params[elem]

        generated_signature = hashlib.sha256(all_params_concatenate.encode("UTF-8")).hexdigest()
        self.config['Signature'] = generated_signature
        return generated_signature
