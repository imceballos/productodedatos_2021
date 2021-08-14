from abc import ABC, abstractmethod
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives \
    import hashes, serialization, padding as SymmetricPadding
from cryptography.hazmat.primitives.asymmetric \
    import padding as AsymmetricPadding
from cryptography.hazmat.primitives.ciphers \
    import algorithms, Cipher, modes
from main.util.crypting.rijndael import RijndaelEcb
from py3rijndael import Pkcs7Padding


class EncryptionAlgorithm(ABC):
    @abstractmethod
    def encrypt(self, message):
        pass

    @abstractmethod
    def decrypt(self, message):
        pass


class VerifyAlgorithm(ABC):
    @abstractmethod
    def sign(self, message):
        pass

    @abstractmethod
    def verify(self, message, signature):
        pass


class RSAAlgorithm(EncryptionAlgorithm, VerifyAlgorithm):
    def __init__(self, keychain):
        if keychain.private:
            self.private_key = serialization.load_pem_private_key(
                keychain.private,
                password=None,
                backend=default_backend()
            )
        if keychain.public:
            self.public_key = serialization.load_pem_public_key(
                keychain.public,
                backend=default_backend()
            )

    def encrypt(self, message):
        return self.public_key.encrypt(
            message,
            AsymmetricPadding.PKCS1v15()
        )

    def decrypt(self, message):
        return self.private_key.decrypt(
            message,
            AsymmetricPadding.PKCS1v15()
        )

    def verify(self, message, signature):
        self.public_key.verify(
            signature,
            message,
            AsymmetricPadding.PKCS1v15(),
            hashes.SHA1()
        )

        return True

    def sign(self, message):
        return self.private_key.sign(
            message,
            AsymmetricPadding.PKCS1v15(),
            hashes.SHA1()
        )


class AESAlgorithm(EncryptionAlgorithm):
    def __init__(self, passphrase):
        self.key = passphrase
        self.block_size = 16  # bytes
        algorithm = algorithms.AES(self.key)
        algorithm.block_size = self.block_size * 8
        self.cipher = Cipher(
            algorithm,
            modes.ECB(),
            backend=default_backend()
        )

    def encrypt(self, message):
        padder = SymmetricPadding.PKCS7(self.block_size * 8).padder()
        encryptor = self.cipher.encryptor()
        padded_data = padder.update(message) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()

    def decrypt(self, crypted_message):
        decryptor = self.cipher.decryptor()
        decrypted_message = decryptor.update(crypted_message) \
            + decryptor.finalize()
        unpadder = SymmetricPadding.PKCS7(self.block_size * 8).unpadder()

        return unpadder.update(decrypted_message) + unpadder.finalize()


class RijndaelAlgorithm(EncryptionAlgorithm):
    def __init__(self, passphrase, block_size=16):
        self.key = passphrase
        self.block_size = block_size
        self.cipher = RijndaelEcb(
            self.key,
            Pkcs7Padding(self.block_size),
            self.block_size
        )

    def encrypt(self, message):
        return self.cipher.encrypt(message)

    def decrypt(self, crypted_message):
        return self.cipher.decrypt(crypted_message)
