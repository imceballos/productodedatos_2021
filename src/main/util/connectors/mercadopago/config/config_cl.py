class MercadopagoConfigCL:
    
    error_url = "/payments/end/mercadopago-itier-cl/failure"
    success_url = "/payments/end/mercadopago-itier-cl/success"
    client_id = "4312213676713856"
    client_secret = "J0AhUiCZ3l4oGH516zb7R5CluvljeEpd"
    currency_code = "CLP"
    sandbox_mode = False
    excluded_payment_types = [{
                                "id": "ticket",
                                "id": "atm"
                            }]
    excluded_payment_methods = [{
                                "id": "khipu"  # excluir medio de pago particular
                            }]
    maximum_installments = 18
    default_installments = 1
    risk_check_enabled = False
    risk_assessor = "accertify"
    refund_limit_days = 90

