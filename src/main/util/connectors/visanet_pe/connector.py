"""Connector Interface"""

from pprint import pprint

import xmltodict
from flask import current_app
from main.util.common_utils import isset
from main.util.connectors.common_connector import CommonConnector
from main.util.connectors.connector import Connector
from main.util.model.payment import PaymentControl
from main.utils.commons_utils import number_format
from main.utils.requests import requests_retry_session


class VisanetPeConnector(CommonConnector, Connector):
    def initialize(self, data: dict, site: str) -> bool:
        return True

    def get_initial_status(self) -> str:
        return 'started'

    def require_additional_info(self) -> bool:
        # TODO
        pass

    def need_redirect(self) -> bool:
        return True

    def get_redirect_data(self, data: dict):
        amount = number_format(data['Payment']['amount'] / 100, 2)
        channel = ''
        email = ''
        frequent_user = ''
        days_of_life = ''
        if 'AdditionalData' in data:
            channel = data['AdditionalData']['channel']
            email = data['AdditionalData']['email']
            frequent_user = data['AdditionalData']['frequentUser']
            days_of_life = data['AdditionalData']['daysOfLife']

        ticket = """<?xml version='1.0' encoding='UTF-8' ?>
                        <nuevo_eticket>
                            <parametros>
                                <parametro id='CANAL'>3</parametro>
                                <parametro id='PRODUCTO'>1</parametro>
                                <parametro id='CODTIENDA'>{}</parametro>
                                <parametro id='NUMORDEN'>{}</parametro>
                                <parametro id='MOUNT'>{}</parametro>
                                <parametro id='DATO_COMERCIO'>{}</parametro>
                                <parametro id='CORREO'>{}</parametro>
                            </parametros>
                            <parametros_antifraude>
                                <parametro_ant id='merchantDefinedData'>
                                    <campo id='field3'>{}</campo>
                                    <campo id='field4'>{}</campo>
                                    <campo id='field21'>{}</campo>
                                    <campo id='field77'>{}</campo>
                                </parametro_ant>
                            </parametros_antifraude>
                        </nuevo_eticket>""".format(self.config.CodTienda, data['Payment']['order_number'],
                                                   amount, data['Payment']['id'], email, channel, email, frequent_user,
                                                   days_of_life)

        url = self.config.WSEticket
        headers = {'content-type': 'application/soap+xml'}
        response = requests_retry_session().post(url, headers=headers, xmlIn=ticket)

        response_json = json.dumps(xmltodict.parse(response.content), indent=4)
        response_json = json.loads(response_json)
        response_json = response_json['GeneraEticketResult']

        current_app.logger.debug(f"[VisanetPe] Result")
        current_app.logger.debug(pprint(response_json))
        if len(response_json) != 0:
            eticket = response_json['eticket']['registro']['campo'][2]['@']
            return {
                'url': self.config.formulario_pago,
                'method': 'POST',
                'enctype': 'application/x-www-form-urlencoded',
                'form_data': {
                    'ETICKET': eticket
                },
                'save_data': {
                    'ETICKET': eticket,
                    'estado': 'PU_ENITIATED'
                }
            }

        redirect_data['url'] = False
        return redirect_data

    def validate_provider_response(self, data: dict, validate_data: dict) -> dict:
        # TODO
        pass

    def process_payment(self, data: dict, payment) -> dict:
        # TODO
        pass

    def process_response_data(self, resp_provider, resp_site, response):
        # TODO
        pass

    def process_end_data(self, status: str, data: dict) -> dict:
        save_data = {}
        if '_post' in data and 'eticket' in data['post']:
            ticket = """<?xml version='1.0' encoding='UTF-8' ?>"
                            <consulta_eticket>
                                <parametros>
                                    <parametro id='CODTIENDA'>{}</parametro>
                                    <parametro id='ETICKET'>{}</parametro>
                                </parametros>
                            </consulta_eticket>""".format(self.config.CodTienda, data['_post']['eticket'])
            url = self.config.WSConsultaEticket
            headers = {'content-type': 'application/soap+xml'}
            response = requests_retry_session().post(url, headers=headers, xmlIn=ticket)
            response_json = json.dumps(xmltodict.parse(response.content), indent=4)
            response_json = json.loads(response_json)
            response = response_json['ConsultaEticketResult']['pedido']['operacion']['campo']
            try:

                if len(response) != 0:
                    save_data['respuesta'] = response[0] if response[0] else ''
                    save_data['estado'] = response[1] if response[1] else ''
                    save_data['cod_tienda'] = response[2] if response[2] else ''
                    save_data['nordent'] = response[3] if response[3] else ''
                    save_data['cod_accion'] = response[4] if response[4] else ''
                    save_data['pan'] = response[5] if response[5] else ''
                    save_data['nombre_th'] = response[6] if response[6] else ''
                    save_data['ori_tarjeta'] = response[7] if response[7] else ''
                    save_data['nom_emisor'] = response[8] if response[8] else ''
                    save_data['eci'] = response[9] if response[9] else ''
                    save_data['dsc_eci'] = response[10] if response[10] else ''
                    save_data['cod_autoriza'] = response[11] if response[11] else ''
                    save_data['cod_rescvv2'] = response[12] if response[12] else ''
                    save_data['id_unico'] = response[13] if response[13] else ''
                    save_data['imp_autorizado'] = response[14] if response[14] else ''
                    save_data['fechayhora_tx'] = response[15] if response[15] else ''
                    save_data['dato_comercio'] = response[18] if response[18] else ''
                else:
                    current_app.logger.fatal(
                        f"[VisanetPe] response failed status: {status} data: {pprint(data, compact=True)}"
                    )
                    return {
                        'status': 'failed'
                    }
                if json_response['respuesta'] == 'AUTORIZADO':
                    return {
                        'transactionId': save_data['dato_comercio'],
                        'saveData': save_data,
                        'status': 'captures'
                    }
                else:
                    current_app.logger.fatal(
                        f"[VisanetPe] response failed status: {status} data: {pprint(data, compact=True)}"
                    )
                    return {
                        'transactionId': save_data['dato_comercio'],
                        'saveData': save_data,
                        'status': 'failed'
                    }
                    pass
            except Exception as exc:
                return {
                    'status': 'failed',
                    'desc': exc
                }
        else:
            current_app.logger.fatal(
                f"[VisanetPe] response failed status: {status} data: {pprint(data, compact=True)}"
            )
            return {
                'status': 'failed',
                'desc': '_post not in data'
            }

        pass

    def process_end_response(
            self, resp_site: str, resp_provider: dict, response
    ) -> dict:
        if resp_site == 'confirmed' and resp_provider['status'] == 'capture':
            return {
                'status': 'captured',
                'save_data': resp_provider['save_data']
            }
        else:
            current_app.logger.fatal(
                f"[VisanetPe] response failed respProvider: {pprint(resp_provider)}"
            )
            return {
                'status': 'failed',
                'save_data': resp_provider['save_data']
            }
        pass

    @staticmethod
    def need_specific_data():
        return False

    @staticmethod
    def can_check_status():
        return True

    def check_status(self, data):
        payments = PaymentControl()
        if len(data) == 0 or data is None:
            return {
                'status': False,
                'desc': 'No data provider'
            }
        conditions = {
            'payments_id': data['Payment']['id']
        }
        provider_data = payments.get_provider_data(
            data["provider"]["id"], conditions
        )

        if 'eticket' in provider_data:
            ticket = """<?xml version='1.0' encoding='UTF-8' ?>"
                                        <consulta_eticket>
                                            <parametros>
                                                <parametro id='CODTIENDA'>{}</parametro>
                                                <parametro id='ETICKET'>{}</parametro>
                                            </parametros>
                                        </consulta_eticket>""".format(self.config.CodTienda,
                                                                      data['_post']['eticket'])
            url = self.config.WSConsultaEticket
            headers = {'content-type': 'application/soap+xml'}
            response = requests_retry_session().post(url, headers=headers, xmlIn=ticket)
            response_json = json.dumps(xmltodict.parse(response.content), indent=4)
            response_json = json.loads(response_json)
            if 'ConsultaEticketResult' in response_json:
                response_json = response_json['ConsultaEticketResult']
                response = []
                if isset(response_json['pedido']['operacion'][0]):
                    for data in response_json['pedido']['operacion']:
                        if data['campo'][0] == 1 and data['campo'][4] == '000':
                            response = data['campo']
                else:
                    response = response_json['pedido']['operacion']['campo']

                if len(response) != 0:
                    save_data['respuesta'] = response[0] if response[0] else ''
                    save_data['estado'] = response[1] if response[1] else ''
                    save_data['cod_tienda'] = response[2] if response[2] else ''
                    save_data['nordent'] = response[3] if response[3] else ''
                    save_data['cod_accion'] = response[4] if response[4] else ''
                    save_data['pan'] = response[5] if response[5] else ''
                    save_data['nombre_th'] = response[6] if response[6] else ''
                    save_data['ori_tarjeta'] = response[7] if response[7] else ''
                    save_data['nom_emisor'] = response[8] if response[8] else ''
                    save_data['eci'] = response[9] if response[9] else ''
                    save_data['dsc_eci'] = response[10] if response[10] else ''
                    save_data['cod_autoriza'] = response[11] if response[11] else ''
                    save_data['cod_rescvv2'] = response[12] if response[12] else ''
                    save_data['id_unico'] = response[13] if response[13] else ''
                    save_data['imp_autorizado'] = response[14] if response[14] else ''
                    save_data['fechayhora_tx'] = response[15] if response[15] else ''
                    save_data['dato_comercio'] = response[18] if response[18] else ''
                else:
                    current_app.logger.fatal(
                        f"[VisanetPe] response was empty for eticket: {pprint(provider_data['eticket'])}"
                    )
                    response = {
                        'status': 'failed'
                    }

                if response[0] == '1' and response[4] == '000':
                    current_app.logger.info(
                        f"[VisanetPe] response was Authorized for eticket: {pprint(provider_data['eticket'])}"
                    )
                    response = {
                        'transactionId': save_data['dato_comercio'],
                        'saveData': save_data,
                        'status': 'captured'
                    }
                else:
                    current_app.logger.fatal(
                        f"[VisanetPe] response failed data: {pprint(data, compact=True)}"
                    )
                    response = {
                        'transactionId': save_data['dato_comercio'],
                        'saveData': save_data,
                        'status': 'failed'
                    }

                if ['capture', 'pending'] in response:
                    site_response = 'confirmed'
                else:
                    site_response = 'failed'

                final_provider_response = self.process_end_response(site_response, response, '')
                final_provider_response['siteResponse'] = site_response
                current_app.logger.fatal(
                    f"[VisanetPe] final response: {pprint(final_provider_response, compact=True)}"
                )
                return final_provider_response;
            else:
                current_app.logger.info(
                    f"[VisanetPe] Eticket get empty answer prom provider {pprint(data['Payment']['id'])}"
                )
                return {
                    'status': False,
                    'desc': 'Eticket response was empty'
                }
        else:
            current_app.logger.fatal("[VisanetPe] Eticket was not Found at DB")
            return {
                'status': False,
                'desc': 'Eticket was not provided'
            }
