from flask import current_app
from main.util.crypting.utils import read_key_file

class Keychain:
    def __init__(self, public_key, private_key):
        self.public_key = read_key_file(public_key)
        self.private_key = read_key_file(private_key)

    @property
    def public(self):
        return self.public_key

    @property
    def private(self):
        return self.private_key


class KeychainFactory:
    @staticmethod
    def create_by_country(country):
        #return current_app.config.get('KEYS_PATH').format(current_app.root_path,current_app.config.get('GROUPON_PUBLIC').format(country.lower()))
        return Keychain(
            public_key=current_app.config.get('GROUPON_PUBLIC').format(
                country.lower()
            ),
            private_key=current_app.config.get('GROUPON_PRIVATE').format(
                country.lower()
            ),
        )

    @staticmethod
    def payments_keys(country):
        return Keychain(
            public_key=current_app.config.get('GROUPON_PUBLIC').format(
                country.lower()
            ),
            private_key=current_app.config.get('PAYMENTS_PRIVATE'),
        )

    @staticmethod
    def napi_keys(country):
        return Keychain(
            public_key=current_app.config.get('PAYMENTS_PUBLIC'),
            private_key=current_app.config.get('GROUPON_PRIVATE').format(
                country.lower()
            ),
        )
