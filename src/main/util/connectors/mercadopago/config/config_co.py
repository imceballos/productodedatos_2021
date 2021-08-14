class MercadopagoConfigCO:
    
    error_url = "/payments/end/mercadopago-itier-co/failure"
    success_url = "/payments/end/mercadopago-itier-co/success"
    client_id = "1849723511427235"
    client_secret = "Z2FJ436LR7gc5ZbsJyreZ9h88lqvO8UM"
    currency_code = "COP"
    sandbox_mode = False
    binary = {'start': "2020-06-19 22:00:00", 'end':"2020-06-19 23:59:59"}
    excluded_payment_types = [{
                                "id": "atm"
                            }]
    excluded_payment_methods = [{
                                "id": "davivienda"  # excluir medio de pago particular
                            }]
    maximum_installments = 24
    default_installments = 1
    risk_check_enabled = False
    risk_assessor = "accertify"
    refund_limit_days = 90

