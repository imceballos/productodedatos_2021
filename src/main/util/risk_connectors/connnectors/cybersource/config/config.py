class CybersourceRiskConfigCL:
    def __init__(self):
        self.merchant_id = "peixe_urbano" 
        self.transaction_key = "IDKbZeoWKvG5KSPkkxvDMm68QZdOQWqaJaaYknJ/wO1lqcFitopwCi90eJQQzlkAmHXLzGJglbd48ZhMYZk4l+hU/k8dWK14r2amt9emuzzUpKqppnzsjLulsHjOzA1ssepvgZ481qGobu1K395OwFd+fafAc+tWBfAoVNc0Gr43gMYrkzX1P7ow8UYnsPaIfVxerlNsrWlMoZPFVbeCbPwzgesSN4rhfvpWomdlcdlA+5mk9BRNp+XKbPVvCXb97A1Wgby8y9bRZJ+yfuaYQqVPNMGZUc9aqWDbo/luHS/YOnd/RfrcDXK53yMW8fTNGEHNZGAR7e7/XHMQn1x/4A=="
        self.wsdl = "https://ics2wstesta.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.161.wsdl"
        self.nvp_wsdl = "https://ics2wstesta.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_NVP_1.161.wsdl"
    def get_config(self):
        config_dict = dict()
        config_dict['merchant_id'] = self.merchant_id
        config_dict['transaction_key'] = self.transaction_key
        config_dict['wsdl'] = self.wsdl
        config_dict['nvp_wsdl'] = self.nvp_wsdl
        return config_dict