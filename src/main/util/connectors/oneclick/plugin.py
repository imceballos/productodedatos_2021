import os
import tbk
from tbk.services import OneClickPaymentService, CommerceIntegrationService
from tbk.commerce import Commerce
from tbk.soap.exceptions import SoapServerException, SoapRequestException
import uuid


class OneClick(OneClickPaymentService, CommerceIntegrationService, Commerce):

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
        self.oneclickservice(normal_commerce)

    def oneclickservice(self, normal_commerce):
        self.oneclick_service = OneClickPaymentService(normal_commerce)
        self.oneclickcommerce_service(self.oneclick_service)

    def oneclickcommerce_service(self, service):
        self.oneclick_commerce_service = CommerceIntegrationService(service)
        
    def initial_inscription(self, data):
        try:
            inscription = self.oneclick_service.init_inscription(**data)
        except SoapServerException:
            inscription = None
        except SoapRequestException:
            inscription = None
        return inscription

    def final_inscription(self, token):
        transaction = self.oneclick_service.finish_inscription(token)
        buy_order = uuid.uuid4().hex[:8]
        return {
            'transaction': transaction,
            'buy_order': buy_order
        }

    def service_authorize(self, data):
        transaction = self.oneclick_service.authorize(**data)
        return {
            'transaction': transaction,
            'buy_order': data['buy_order'], 
            'amount': data['amount']
        }
    
    def service_nullify(self, data):
        nullify = self.oneclick_commerce_service.nullify(**data)
        return nullify

    def service_release(self, data):
        release = self.oneclick_service.code_reverse_oneclick(**data)
        return release