from main.util.crypting.algorithms import RijndaelEcb, RSAAlgorithm
from main.util.crypting.keychain import Keychain
from main.util.crypting.utils import random_string
from py3rijndael import Pkcs7Padding
# Wrapper classes for the algorithms


class Encryptor:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def encrypt(self, message):
        return self.algorithm.encrypt(message)

    def decrypt(self, message):
        return self.algorithm.decrypt(message)


class VerifyEncryptor(Encryptor):
    def verify(self, message, signature):
        return self.algorithm.verify(message, signature)

    def sign(self, message):
        return self.algorithm.sign(message)


class RSAEncryptor(VerifyEncryptor):
    def __init__(self, keychain: Keychain):
        super().__init__(RSAAlgorithm(keychain))


class RijndaelECBEncryptor(VerifyEncryptor):
    def __init__(self, block_size, key=random_string(32)):
        self.key = key
        super().__init__(RijndaelEcb(bytes(self.key, 'ascii'),
                                     Pkcs7Padding(block_size), block_size))
