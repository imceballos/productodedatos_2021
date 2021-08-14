from main.util.connectors.connector_field_map import ConnectorFieldMap


class VisanetPeFieldMap(ConnectorFieldMap):
    config = {
        "auth_code": "cod_autoriza",
        "card_last_numbers": "",
        "card_owner": "nombre_th",
        "commerce_code": "",
        "installments": "",
        "payment_franchise": "",
    }