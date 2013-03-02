import base64

from Crypto.Cipher import ARC4

IV = 'xxxxxxxx'

def encrypt(plaintext):
    if not plaintext:
        return ''
    arc = ARC4.new(IV)
    ciphertext = arc.encrypt(plaintext)
    return base64.b64encode(b''+ciphertext)

def decrypt(ciphertext):
    if not ciphertext:
        return ''
    ciphertext = base64.b64decode(b''+ciphertext)
    arc = ARC4.new(IV)
    plaintext = arc.decrypt(ciphertext)
    return plaintext