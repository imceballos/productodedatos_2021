from cryptography.exceptions import InvalidSignature
from main.util.crypting.algorithms import RijndaelAlgorithm
from main.util.crypting.encryptors import RSAEncryptor, RijndaelECBEncryptor
from main.util.crypting.keychain import KeychainFactory
import base64
import json


class EncryptionUtils:
    @staticmethod
    def decrypt_payment_payload_from_napi(payload, country):
        billing_order = payload.get('order', {}).get('billingRecord', {})
        if billing_order.get('formParameters') is None:
            return {}

        form_parameters = payload['order']['billingRecord']['formParameters']

        return EncryptionUtils.decrypt_form_parameters_to_payments(
            form_parameters,
            country
        )

    @staticmethod
    def decrypt_form_parameters_to_payments(payload, country):
        return EncryptionLogics(KeychainFactory.payments_keys(country))\
            .decrypt_data(payload)

    @staticmethod
    def encrypt_form_parameters_to_payments(payload, country, res_url):
        data = EncryptionUtils.encrypt_data_to_payments(payload, country)
        data['resUrl'] = res_url

        return data

    @staticmethod
    def encrypt_data_to_payments(payload, country):
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        message = bytes(payload, 'ascii')

        return EncryptionLogics(KeychainFactory.napi_keys(country)) \
            .symmetric_encrypt(message)

    @staticmethod
    def decrypt_data_from_payments(payload, country):
        return EncryptionLogics(KeychainFactory.napi_keys(country)) \
            .decrypt_data(payload)

    @staticmethod
    def encrypt_data_from_payments(payload, country):
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        message = bytes(payload, 'ascii')

        return EncryptionLogics(KeychainFactory.payments_keys(country)) \
            .asymmetric_encrypt(message)


class EncryptionLogics:
    def __init__(self, keychain):
        self.keychain = keychain

    def decrypt_data(self, data):
        if data.get('enckey'):
            data = self.symmetric_decrypt(data)
        else:
            data = self.asymmetric_decrypt(data)

        return json.loads(data)

    def symmetric_encrypt(self, message):
        rijndael = RijndaelECBEncryptor(32)
        data = self.asymmetric_encrypt(bytes(rijndael.key, 'ascii'))
        enc_data = base64.b64encode(base64.b64encode(
            rijndael.encrypt(message)
        ))
        data['enckey'] = data.get('encdata')
        data['encdata'] = enc_data.decode("utf-8")

        return data

    def symmetric_decrypt(self, data):
        asymmetric_data = {
            'encdata': data.get('enckey'),
            'signature': data.get('signature')
        }
        # decrypt key with asymmetric decryption
        key = self.asymmetric_decrypt(asymmetric_data)

        key_bytes = bytes(key, 'ascii')
        rijndael = RijndaelAlgorithm(key_bytes, 32)
        b64_data = base64.b64decode(base64.b64decode(data['encdata']))
        enc_data = rijndael.decrypt(b64_data)

        return enc_data.decode("utf-8")

    def asymmetric_encrypt(self, data):
        encryptor = RSAEncryptor(self.keychain)
        enc_data = base64.b64encode(encryptor.encrypt(data))
        signature = base64.b64encode(encryptor.sign(data))
        return {
            'encdata': enc_data.decode("utf-8"),  # Aqui los datos encriptados,
            'signature': signature.decode("utf-8")  # Aqui la firma
        }

    def asymmetric_decrypt(self, data):
        decryptor = RSAEncryptor(self.keychain)
        binary_data = base64.b64decode(data.get('encdata'))
        b64_signature = base64.b64decode(data.get('signature'))
        try:
            text = decryptor.decrypt(binary_data)
        except ValueError:
            raise ValueError('asymmetric_decryp - Decryption Error')

        self.verify_signature(decryptor, text, b64_signature)

        return text.decode('ascii')

    def verify_signature(self, decryptor, data, signature):
        try:
            decryptor.verify(data, signature)
        except InvalidSignature:
            raise ValueError('verify_signature - Decryption Error')

        return True
