from py3rijndael import Rijndael
from py3rijndael.paddings import PaddingBase


class RijndaelEcb(Rijndael):
    def __init__(self, key: bytes, padding: PaddingBase, block_size: int = 16):
        super().__init__(key=key, block_size=block_size)
        self.padding = padding

    def encrypt(self, source: bytes):
        ppt = self.padding.encode(source)
        offset = 0
        ct = bytes()
        while offset < len(ppt):
            block = ppt[offset:offset + self.block_size]
            block = super().encrypt(block)
            ct += block
            offset += self.block_size

        return ct

    def decrypt(self, cipher):
        assert len(cipher) % self.block_size == 0
        ppt = bytes()
        offset = 0
        while offset < len(cipher):
            block = cipher[offset:offset + self.block_size]
            ppt += super().decrypt(block)
            offset += self.block_size

        pt = self.padding.decode(ppt)
        return pt
