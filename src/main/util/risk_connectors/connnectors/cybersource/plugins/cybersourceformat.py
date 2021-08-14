class CybersourceFormat:

    def __init__(self):
        self.fields = dict()
      
    def formatPurchaseTotalData(self, purchaseData):

        self.fields["purchaseTotals_currency"] = purchaseData['currency']
        self.fields["purchaseTotals_grandTotalAmount"] = round(purchaseData['Payment']['amount']/100, 2)
        
    def formatItemData(self, itemData):
        for i, item in enumerate(itemData):
            self.fields["item_" + str(i) + "_productName"] = item['product_name']
            self.fields["item_" + str(i) + "_productCode"] = item['product_code']
            self.fields["item_" + str(i) + "_unitPrice"] = item['product_unitprice']
            self.fields["item_" + str(i) + "_productSKU"] = item['product_sku']
            self.fields["item_" + str(i) + "_quantity"] = item['product_quantity']
        

    def formatBillingData(self, billingData):
        
        self.fields["billTo_city"] = "Mountain View"
        self.fields["billTo_country"] = "US"
        self.fields["billTo_email"] = billingData['AdditionalData']['user']['email'] if billingData['AdditionalData']['user']['email'] else "null@cybersource.com" 
        self.fields["billTo_firstName"] = "NOREAL"
        self.fields["billTo_lastName"] = "NAME"
        self.fields["billTo_postalCode"] = 94043
        self.fields["billTo_state"] = "CA"
        self.fields["billTo_street1"] = "1295 Charleston Rd"
        self.fields["billTo_street2"] = ""
        self.fields["billTo_phoneNumber"] = ""
        self.fields["billTo_customerID"] = billingData['AdditionalData']['user']['id'] if billingData['AdditionalData']['user']['id'] else ""
        self.fields["billTo_ipAddress"] = billingData['AdditionalData']['user']['IP'] if billingData['AdditionalData']['user']['IP'] else ""
        
    def formatCreditCardData(self, creditCardData = ""):

        self.fields["card_accountNumber"] = "4111111111111111" if creditCardData == "" else creditCardData['card_accountNumber']
        self.fields["card_expirationMonth"] = "12" if creditCardData == "" else creditCardData['card_expirationMonth']
        self.fields["card_expirationYear"] = "2028" if creditCardData == "" else creditCardData['card_expirationYear']
        self.fields["card_cvNumber"] = ""

    def formatShipToData(self, shipToData):

        self.fields["shipTo_firstName"] = shipToData['AdditionalData']['user']['first_name'] if shipToData['AdditionalData']['user']['first_name'] else ""
        self.fields["shipTo_lastName"] = shipToData['AdditionalData']['user']['last_name'] if shipToData['AdditionalData']['user']['last_name'] else ""
        self.fields["shipTo_postalCode"] = ""
        self.fields["shipTo_city"] = ""
        self.fields["shipTo_country"]  = shipToData['AdditionalData']['order']['shippingCountry'] if shipToData['AdditionalData']['order']['shippingCountry'] else ""
        self.fields["shipTo_state"] = shipToData['AdditionalData']['order']['state'] if shipToData['AdditionalData']['order']['state'] else ""
        self.fields["shipTo_street1"] = shipToData['AdditionalData']['order']['shippingAddress1'] if shipToData['AdditionalData']['order']['shippingAddress1'] else ""
        self.fields["shipTo_street2"] = shipToData['AdditionalData']['order']['shippingAddress2'] if shipToData['AdditionalData']['order']['shippingAddress2'] else ""
        self.fields["shipTo_phoneNumber"] = shipToData['AdditionalData']['phoneNumber'] if shipToData['AdditionalData']['phoneNumber'] else ""


    def createFields(self, purchaseData, itemData, billingData, shipToData):

        self.formatPurchaseTotalData(purchaseData)
        self.formatItemData(itemData)
        self.formatBillingData(billingData)
        self.formatCreditCardData()
        self.formatShipToData(shipToData)

