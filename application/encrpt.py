from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import padding
from os import urandom

# key = urandom(32) # uncomment and replace it with your key if you do not want to use a file

# comment the following if you want to place key in the variable
#key_f = open('./key/key.txt')
#keys = str(key_f.read())
with open('./key/key.txt', 'rb') as file:
    key = file.read()

# print(keys)

def conv_key(key):
    byte_array = key.encode('utf-8')
    # Adjust the length to 32 bytes
    if len(byte_array) >= 32:
        return byte_array[:32]  # Truncate to 32 bytes
    else:
        return byte_array.ljust(32, b'\x00')  # Pad with zeros to make it 32 bytes

#key = conv_key(keys)
print(f'loaded key = {key}')


def encrypt_aes_gcm(plaintext, key):
    # Generate a random IV
    iv = urandom(12)  # Standard size for AES-GCM
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
   
    # Encrypt plaintext
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return iv + ciphertext + encryptor.tag  # Combine IV, ciphertext, and tag

def decrypt_aes_gcm(ciphertext, key):
    iv = ciphertext[:12]  # Extract IV
    tag = ciphertext[-16:]  # Extract tag
    encrypted_data = ciphertext[12:-16]  # Extract ciphertext
   
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
   
    return decryptor.update(encrypted_data) + decryptor.finalize()


if __name__ == '__main__':
    # Example usage
    # key = urandom(32)  # We will generate our own key so please document where you stored your key in readme.md
    plaintext = b"22"  # NHI

    encrypted = encrypt_aes_gcm(plaintext, key)
    decrypted = decrypt_aes_gcm(encrypted, key)

    print(key)  # Output: b'22'p
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)
