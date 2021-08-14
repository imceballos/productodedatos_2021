from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.transports import Transport
from config.config import CybersourceRiskConfigCL
from plugins.cybersourceformat import CybersourceFormat

class CybersourceriskConnector(CybersourceFormat):

    def __init__(self, data):
        
        super().__init__()
        configs = CybersourceRiskConfigCL().get_config()

        self.data = data
        self.fields['merchantID'] = configs['merchant_id']
        self.client = Client(configs['nvp_wsdl'], transport=Transport(cache=None), wsse = UsernameToken(configs['merchant_id'], configs['transaction_key']))
        #TODO set Headers
        
    def assess(self, payment):
        
        self.fields["deviceFingerprintID"] = self.data['AdditionalData']['order']['cookie']
        self.fields["ccAuthService_run"] = "true"
        self.fields["afsService_run"] = "true"
        self.fields["merchantDefinedData_mddField_1"] = "Website"
        self.fields["merchantReferenceCode"] = payment['Payment']['id']

        self.createFields(self.data['purchaseData'], self.data['itemData'], self.data, self.data)

        authMessage = self.formatMessage()
        responseTransaction = self.createTransaction(authMessage)
        if responseTransaction:
            final_response = self.proccesResult(responseTransaction)
        
        return final_response


    def formatMessage(self):
        authMessage = '\n'.join(["{}={}".format(key, value) for key, value in self.fields.items()])
        return authMessage

    def createTransaction(self, authMessage):
        try:
            result = self.client.service.runTransaction(authMessage)
        except:
            return False
        return result
        
    def proccesResult(self, responseTransaction):
        response = dict()
        for x in responseTransaction.split('\n'):
            if '=' in x:
                key, value = x.split('=')
                response[key] = value
        return response 

