import requests
import os
import tbk
from tbk.services import WebpayService
from tbk.commerce import Commerce

class WebpayPlus(WebpayService, Commerce):

    def __init__(self, commerce_code):
        self.commerce_code = commerce_code
        self.load_commerce(commerce_code)

    def load_commerce(self, commerce_code):
        CERTIFICATES_DIR = os.path.join(os.path.dirname(__file__), "commerces")
        with open(
            os.path.join(CERTIFICATES_DIR, commerce_code, commerce_code + ".key"), "r"
        ) as file:
            key_data = file.read()
        with open(
            os.path.join(CERTIFICATES_DIR, commerce_code, commerce_code + ".crt"), "r"
        ) as file:
            cert_data = file.read()
        with open(os.path.join(CERTIFICATES_DIR, "tbk.pem"), "r") as file:
            tbk_cert_data = file.read()

        load_commerce_data = {
                                'commmerce_code': commerce_code,
                                'key_data': key_data,
                                'cert_data': cert_data,
                                'tbk_cert_data': tbk_cert_data,
                                'environment': 'DEVELOPMENT'
                             }

        self.load_commerce_data = load_commerce_data
        self.normal_commerce(load_commerce_data)

    def normal_commerce(self, load_commerce_data):
        normal_commerce = Commerce( commerce_code=load_commerce_data['commmerce_code'],
                                    key_data=load_commerce_data["key_data"],
                                    cert_data=load_commerce_data["cert_data"],
                                    tbk_cert_data=load_commerce_data["tbk_cert_data"],
                                    environment='DEVELOPMENT')
        self.normal_commerce_data = normal_commerce
        self.start_transaction(normal_commerce)

    def start_transaction(self, normal_commerce):
        self.first_transaction = WebpayService(normal_commerce)

    def initial_transaction(self, data):
        transaction = self.first_transaction.init_transaction(**data['webpay'])
        return {
                'token': transaction['token'],
                'url': transaction['url']
                }

    def gettransaction_result(self, token):
        return self.first_transaction.get_transaction_result(token)

    def acknowledgetransaction(self, token):
        return self.first_transaction.acknowledge_transaction(token)


