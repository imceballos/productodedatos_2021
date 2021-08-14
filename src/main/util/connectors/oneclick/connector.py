import pprint

from .plugin import OneClick
from main import db
from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector
from main.models.models import UsersOneclick
from flask import current_app

class OneClickConnector(CommonConnector, Connector):

    def __init__(self, commerce_code):
        self.one_click = self.create_oclick(commerce_code)
       
    def create_oclick(self, commerce_code):
        one_click = OneClick(commerce_code)
        return one_click

    def initialInscription(self, data):
        transaction = self.one_click.initial_inscription(data)
        return transaction

    def finalIscription(self, token):
        transaction = self.one_click.final_inscription(token)
        return transaction

    def serviceAuthorize(self, data):
        transaction = self.one_click.service_authorize(data)
        return transaction

    def serviceNullify(self, data):
        nullify = self.one_click.service_nullify(data)
        return nullify

    def initialize(self, data, site):
        self.data = data
        if 'amount' not in data.keys():
            return False
        userOneclick = self.findByUserIdAndSiteId(data['user_id'], site['Site']['id'])
        if userOneclick:
            email = 'info@groupon.cl' if data['AdditionalData']['email'] is None else data['AdditionalData']['email']
            responseUrl = current_app.config.get("RESPONSE_URL")
            data_initial_inscription = {
                                        'userId': data['user_id'], 
                                        'email': email,
                                        'response_url': responseUrl
                                        }

            inscription = self.initialInscription(data_initial_inscription)
            token = inscription['token']

            if token:
                initInscription = UsersOneclick(site_id = site['Site']['id'], user_id = data['user_id'], active = 3,
                                                init_token = token, init_data = data['_post'])
                
                db.session.add(initInscription)
                db.session.commit()

                return  {
                    'url' : responseUrl,
                    'method' : 'POST',
                    'enctype' : 'application/x-www-form-urlencoded',
                    'form_data': {'TBK_TOKEN' : token},
                    'redirect' : True
                        }  

            current_app.logger.error("[OneclickTransbank] empty token")
            return False  

        data['UsersOneclick'] = userOneclick
        return True

    def getInitialStatus(self):
        return 'started'
   	
    def requiredAdditionalInfo(self):
        return False
    
    def needRedirect(self):
        return False

    def hasExpressSubscription(self):
        return False

    def getRedirectData(self, data):
        return None

    def getAdditionalFields(self):
        return {
            {
                'label' : ('Nombre'),
                'name' : 'name',
                'type' : 'text',
                'validation' : {
                    'required' : 'true',
                    'maxlength' : 50
                }
            }
        }

    def validateAdditionalData(self, data):
        return None

    def validateProviderResponse(self, data, validateData):
        return None

    def processResponseData(self, respProvider, respSite, response):
        return None

    def processEndData(self, status, data):
        if (data['dataOneClick'] and isinstance( data['dataOneClick'], list)):
            return {
                'transactionId' : data['Payment']['id'],
                'saveData' : data['dataOneClick'],
                'status' : 'captured'                
            }
        elif (data['dataOneClick'] and isinstance(data['dataOneClick'], str)):

            current_app.logger.error(
                "[OneclickTransbank] response failed status=" + status + "data= " +  pprint.pprint(data, compact=True)
                )
            return {
                'transactionId' : data['Payment']['id'],
                'saveData' : data['dataOneClick'],
                'status' : 'failed'                
            }
        else:
            current_app.logger.error(
                "[OneclickTransbank] response failed status=" + status + "data= " +  pprint.pprint(data, compact=True)
                )
            return {
                'transactionId' : data['Payment']['id'],
                'status' : 'failed'                
            }

    def processEndResponse(self, respSite, respProvider, response):
        if (respSite == 'confirmed' and respProvider['status'] == 'captured'):
            return {
                'status' : 'captured',
                'saveData': respProvider['saveData']
            }
        elif respProvider['saveData']:
            current_app.logger.error(
                "[OneclickTransbank] response failed respSite=" + respSite + "respProvider= " +  pprint.pprint(respProvider, compact=True)
                )
            return {
                'status' : 'failed',
                'saveData': respProvider['saveData']
            }
        else:
            current_app.logger.error(
                "[OneclickTransbank] response failed respSite=" + respSite + "respProvider= " +  pprint.pprint(respProvider, compact=True)
                )
            return {
                'status' : 'failed'
            }

    def processPayment(self, data, payment):
        data_service_authorize = {
                                    'buy_order': data['buy_order'],
                                    'tbk_user': data['UsersOneclick']['tbkUser'],
                                    'amount': payment['Payment']['amount']/100,
                                    'username' : data['username']
                                }

        ocp = self.one_click.service_authorize(data_service_authorize)
        if (ocp and ocp['responseCode'] == 0):
            data['dataOneClick']['user_id'] = data['UsersOneclick']['id']
            data['dataOneClick']['tbkUser'] = data['UsersOneclick']['tbkUser']
            data['dataOneClick']['amount'] = payment['Payment']['amount']
            data['dataOneClick']['authorizationCode'] = ocp['authorizationCode']
            data['dataOneClick']['responseCode'] = ocp['responseCode']
            data['dataOneClick']['creditCardType'] = ocp['creditCardType']
            data['dataOneClick']['last4CardDigits'] = ocp['last4CardDigits']
            data['dataOneClick']['transactionId'] = ocp['transactionId']

        elif (ocp and ocp['responseCode'] != 0):
            return {
                'status' : 'failed',
                'saveData': ocp
                }
        else:
            return {
                'status': 'failed'
            }           
        return {
            'status' : 'success'
            }
    
    def getConfig(self):
        return self.Config

    def getKeyPath(self):
        return self.keyPath

    def processGetProvider(self, userId, siteId, provider):
        userOneclick = self.findByUserIdAndSiteId(userId, siteId)
        if userOneclick:
            provider['extra']['creditCardType'] = userOneclick['UsersOneclick']['creditCardType']
            provider['extra']['Last4CardDigits'] = userOneclick['UsersOneclick']['Last4CardDigits']
            provider['extra']['oneClickUser'] = userOneclick['UsersOneclick']['id']
        return provider
        

    def findByUserIdAndSiteId(self, userId, siteId):
        userOneclick = UsersOneclick.find_by_userid_siteid(userId, siteId)
        return userOneclick

    def findByUserIdAndtbkUser(self, userId, tbkUser):
        userOneclick = UsersOneclick.find_by_userid_tbkuser(userId, tbkUser)
        return userOneclick

    def startInscription(self, site_id, user_id, mail = 'info@groupon.cl'):
        responseUrl = current_app.config.get("RESPONSE_URL")
        data_initial_inscription = {
                                    'userId': user_id, 
                                    'email': mail,
                                    'response_url': responseUrl
                                    }

        inscription = self.initialInscription(data_initial_inscription)
        token = inscription['token']
        if not token:
              current_app.logger.error(
                "[OneclickTransbank] empty token " +  token
                )
        return token


    def processReturnUserData(self, data):
        return_data = {}
        return_data['user_id']  = data['UsersOneclick']['user_id']
        return_data['creditCardType']  = data['UsersOneclick']['creditCardType']
        return_data['last4CardDigits']  = data['UsersOneclick']['last4CardDigits']
        return_data['tbkUser']  = data['UsersOneclick']['tbkUser']
        return return_data

    def disable(self, user):
        ocp = self.findByUserIdAndtbkUser(user['UsersOneclick']['user_id'], user['UsersOneclick']['tbkUser'])
        if ocp:
            data = UsersOneclick(id = user['UsersOneclick']['id'], active = 0)       
            db.session.add(data)
            db.session.commit()
            return True

        current_app.logger.error(
                "[OneclickTransbank] disable_error " +  pprint.pprint(ocp, compact= True)
                )
        return False

    def start_subscription(self, data):
        if data['submit'] is not None:
            responseUrl = current_app.config.get("RESPONSE_URL")

            return {
                'url': responseUrl,
                'method': 'POST',
                'enctype': 'application/x-www-form-urlencoded',
                'form_data': {'TBK_TOKEN': data['submit']},
                'redirect': True
                }
        return False


    def finish_subscription(self, data):
        token = data['token']
        user_id = data['user_id']
        site_id = data['site_id']

        result = self.finalIscription(token)
        if (result and result['responseCode'] == 0):
            user = UsersOneclick(id = data['id'], site_id = site_id, user_id = user_id, active = 1, 
                                authCode = result['authCode'], creditCardType= result['creditCardType'], 
                                last4CardDigits = result['last4CardDigits'], tbkUser = result['creditCardType'])
            db.session.add(user)
            db.session.commit()
            userOneclick = self.findByUserIdAndSiteId(user_id, site_id)
            data['UsersOneclick'] = userOneclick['UsersOneclick']
            return True

        current_app.logger.error(
                "[OneclickTransbank] empty result " +  pprint.pprint(result, compact= True)
                )
        return False

    def validateFinishData(self, request, data):
        if request['TBK_TOKEN'] is None:
            current_app.logger.error(
                "[OneclickTransbank] Empty TBK_TOKEN"
                )
            return False
        if data['submit'] is None:
            current_app.logger.error(
                "[OneclickTransbank] Empty session data: " +  request['TBK_TOKEN']
                )
            return False

        data['token'] = request['TBK_TOKEN']
        data['user_id'] = data['user_id']
        data['site_id'] = data['site_id']

        return data