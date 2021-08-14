class PaypalConfigMX:
    # Config original que tenia en el archivo de configuracion de Connectors-conf-dev
    url                     = 'https://www.sandbox.paypal.com/webscr'
    error_url               = '/payments/end/paypal-itier-mx/failure'
    success_url             = '/payments/end/paypal-itier-mx/success'
    version	                = '2.3'
    need_additional_info    = False
    redirect                = True
    confirmation_required   = False
    api_endpoint            = 'https://api-3t.sandbox.paypal.com/nvp'
    api_username            = 'needish-payment-portal_api1.grouponlatam.com'
    api_password            = 'A8B2JJDXNMVQGVBR'
    api_signature           = 'AFcWxV21C7fd0v3bYYYRCpSSRl31ADH-NA8OylHKs3PXSnXXsj7PiFWS'
    salt                    = 'd3dd319317abb437f18d3fdb3f0f2e66'
    risk_check_enabled      = False
    risk_assessor           = 'accertify'
    # Config nueva que Yissus tenia en su .env
    URL_PAYPAL              = 'https://api.sandbox.paypal.com/'
    PAYPAL_SECRET_ID        = 'EEnJnTjI2oltDJYlPQkd98zPAdpfqaonjvgEnvb5feI3_3NOihDRsS9y5ld2PBJMU7OY9liy5FeUkwUx'
    PAYPAL_CLIENT_ID        = 'AYJokM8J9KTFS3e_vbDRvVF_Rs5_Qpb2GqcDW1VTxOKLkq7VR0gzUM4SjQ1iJ6on0J4j-2FhbeykRNrx'