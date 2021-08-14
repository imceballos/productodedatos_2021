class SafetyPayConfigPe:

    country = "Pe"
    apiKey =  '4fd64f126b84c4ea28f4bf2326747d96',
    signatureKey = 'ace79bcdb854b0788d7f6a523f44561e',
    currencyCode =  'PEN',
    language = 'ES',
    createExpressToken = 'https://sandbox-mws2.safetypay.com/express/ws/v.3.0/Post/CreateExpressToken',
    createRefundProcess = 'https://sandbox-mws2.safetypay.com/express/ws/v.3.0/Post/CreateRefundProcess',
    getOperation = 'https://sandbox-mws2.safetypay.com/express/ws/v.3.0/Post/GetOperation',
    error_url = '/payments/end/safetypay/failure',
    success_url = '/payments/end/safetypay/success',
    expirationTime = 1440,
    risk_check_enabled = True,
    risk_assessor = 'accertify'


