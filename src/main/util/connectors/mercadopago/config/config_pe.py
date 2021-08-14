class MercadopagoConfigPE:
    
    error_url = "/payments/end/mercadopago-itier-pe/failure"
    success_url = "/payments/end/mercadopago-itier-pe/success"
    client_id = "5327093434009284"
    client_secret = "swLLrTHOhbVQDIwREzQJlNkD42hf5F5T"
    currency_code = "PEN"
    sandbox_mode = False
    excluded_payment_types = [{
                                "id": "atm"
                            }]
    maximum_installments = 24
    default_installments = 1
    risk_check_enabled = False
    risk_assessor = "accertify"
    refund_limit_days = 90

