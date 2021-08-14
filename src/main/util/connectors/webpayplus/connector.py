from datetime import datetime
import pytz
import locale

from .plugin import WebpayPlus
from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector
from main.models.payments_db import Payment, DataWebpayPlus

class WebpayPlusConnector(CommonConnector, Connector):

    def __init__(self, commerce_code):
        self.webpay_plus = self.create_wplus(commerce_code)
        self.data = {}
       
    def create_wplus(self, commerce_code):
        webpay_plus = WebpayPlus(commerce_code)
        return webpay_plus

    def isDuplicate(self, siteId, order_number):
        return Payment.find_by_siteid_order(siteId, order_number)

    def initial_validation(self, data, site):
        if not 'amount' in data.keys():
            return False
        if self.isDuplicate(site['id'], data['buy_order']):
            return False
        self.data['webpay'] = {
                        'amount': data['amount'],
                        'buy_order': data['buy_order'],
                        'return_url': "http://localhost:23006/pages/return",
                        'final_url': "http://localhost:23006/pages/final",
                        'session_id': data['session_id']
                        }
        return True
    
    def initialize(self, data, site):
        if self.initial_validation(data, site):
            transaction = self.webpay_plus.initial_transaction(self.data)
            try:
                self.data['initTransactionOutput'] = {
                            'token': transaction['token'],
                            'url': transaction['url']
                                                    }
                return True
            except:
                return False
        return False

    def getInitialStatus(self):
        return 'started'

    def requireAdditionalInfo(self):
	    return 'additional_info'

    def needRedirect(self):
        return 'redirect'

    def getRedirectData(self, data):
        return {
                'url' : data['initTransactionOutput']['url'],
                'method' :'POST',
                'enctype' : 'application/x-www-form-urlencoded',
                'form_data' : {'token_ws' : data['initTransactionOutput']['token']}
                }

    def getPaymentId(self, data):
        return True

    def validateProviderResponse(self, data, validateData):
        return True

    def processPayment(self, data, payment):
        return True
        
    def processResponseData(self, respProvider, respSite, response):
        return True

    def proccessEndData(self, status, data):
        if status == 'finish':
            if 'buy_order' in data['webpay'].keys():
                return {
                    'transactionId': self.findPaymentIdByOrderNumber(data['webpay']['buy_order']),
                    'saveData': {},
                    'redirect': {},
                    'status': 'failed'
                }
            else:
                providerData = self.getProviderData(data['initTransactionOutput']['token'])
                return {
                    'transactionId' : providerData['payment_id'],
                    'saveData' : {},
                    'status' : 'captured' if providerData['response_code'] == 0 else 'failed'
                        }

        saveData = {}
        redirect = {}
        result = {}
        status = 'failed'
        transactionId = None
        if 'token' in data['webpay'].keys():
            result = self.getTransactionResult(data['webpay']['token'])
        if result:
            saveData['accounting_date'] = result['transaction']['accountingDate']
            saveData['buy_order'] = result['transaction']['buyOrder']
            saveData['card_number'] = result['transaction']['cardDetail']['cardNumber']
            saveData['card_expiration_date'] = result['transaction']['cardDetail']['cardExpirationDate']
            saveData['authorization_code'] = result['transaction']['detailOutput'][0]['authorizationCode']
            saveData['payment_type_code'] = result['transaction']['detailOutput'][0]['paymentTypeCode']
            saveData['response_code'] = result['transaction']['detailOutput'][0]['responseCode']
            saveData['shares_number'] = result['transaction']['detailOutput'][0]['sharesNumber']
            saveData['amount'] = result['transaction']['detailOutput'][0]['amount']
            saveData['commerce_code'] = result['transaction']['detailOutput'][0]['commerceCode']
            saveData['session_id'] = result['transaction']['sessionId']
            saveData['transaction_date'] = result['transaction']['transactionDate']
            saveData['vci'] = result['transaction']['VCI']
            saveData['token'] = result['token']

            if result['transaction']['detailOutput'][0]['responseCode'] !=0:
                saveData['response_description'] = result['transaction']['detailOutput'][0]['responseDescription']
        
            redirect = {
                    'url' : result['transaction']['urlRedirection'],
                    'method' :'POST',
                    'enctype' : 'application/x-www-form-urlencoded',
                    'form_data' : {'token_ws' : result['token']}
            }
            transactionId = self.findPaymentIdByOrderNumber(saveData['buy_order'])
            status = 'captured' if result['transaction']['detailOutput'][0]['responseCode'] == 0 else 'failed'

            return {
                'transactionId' : transactionId,
                'saveData' : saveData,
                'redirect' : redirect,
                'status' : status
            }

    def proccessEndResponse(self, respSite, respProvider, response):
        if (respSite == 'confirmed' and respProvider['status'] == 'captured'):
            return {
                'status' : 'captured',
                'saveData': respProvider['saveData']
            }
        elif ('saveData' in respProvider.keys()):
            return {
                'status' : 'failed',
                'saveData' : respProvider['saveData']
            }
        else:
            return {
                'status' : 'failed'
            }

    def findPaymentIdByOrderNumber(self, orderNumber):
        return Payment.find_id_by_ordernumber(orderNumber)
        
    def getProviderData(self, token):
        return DataWebpayPlus.find_by_token(token)
    
    def getTransactionResult(self, token):
        try:
            transaction = self.webpay_plus.gettransaction_result(token)
            transaction_detail = transaction["detailOutput"]
            self.webpay_plus.acknowledgetransaction(token)
            return {
                'transaction': transaction,
                'transaction_detail': transaction_detail,
                'token': token
                }
        except:
            return None
    

