"""PayPal Field Map Class"""

from src.main.util.connectors.connector_field_map import ConnectorFieldMap


class PayPalFieldMap(ConnectorFieldMap):
    config = {
        'auth_code': '',
        'card_last_numbers': '',
        'card_owner': '',
        'commerce_code': '',
        'installments': '',
        'payment_franchise': '',
    }
    pass
