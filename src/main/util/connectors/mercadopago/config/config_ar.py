class MercadopagoConfigAR:
    
    error_url = "/payments/end/mercadopago-itier-ar/failure"
    success_url = "/payments/end/mercadopago-itier-ar/success"
    client_id = "851355601295937"
    client_secret = "Hp00H8E92taEpVZEYWcuRp0BCLjpegnx"
    currency_code = "ARS"
    sandbox_mode = False
    excluded_payment_types = [{
                                "id": "atm"
                            }]
    maximum_installments = 24
    default_installments = 1
    risk_check_enabled = False
    risk_assessor = "accertify"
    refund_limit_days = 90

