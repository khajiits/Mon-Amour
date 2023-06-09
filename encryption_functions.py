from Crypto.Cipher import AES
from Crypto.Util import Counter

import hash_functions as hf
import mac_functions as mf


BLOCK_SIZE = 16  # in bytes
HMAC_SIZE = 32  # in bytes


def encrypt_message(message: str, secret_key: str) -> tuple[int, bytes, bytes]:
    """Encrypts the message using the AES algorithm in CTR mode.

    The answer to the question imposed is sent to the hashing function where it will be hashed for 15 seconds (default) together with a 16-byte pseudo-randomly generated salt.
    A 16-byte counter is also generated and used in the AES algorithm in CTR mode to encrypt the message.
    In the end, the number of hashing iterations, the salt generated and the encrypted ciphertext are returned.

    Args:
        message (str): Message to be encrypted.
        secret_key (str): Secret key to encrypt the message.

    Returns:
        tuple[int, bytes, bytes]: A tuple containing the number of hashing iterations, the salt and the encrypted ciphertext.
    """
    iter_counter, salt, key = hf.generate_hash(secret_key)
    counter = Counter.new(nbits=BLOCK_SIZE*8)
    
    cipher = AES.new(key, AES.MODE_CTR, counter=counter)
    ciphertext: bytes = cipher.encrypt(message.encode())
    
    return iter_counter, salt, ciphertext


def decrypt_message(password: str, input: list[str]) -> tuple[str, bool] | tuple[None, None]:
    """Decrypts the ciphertext using the AES algorithm in CTR mode.

    The answer given by the recipient is sent to the hashing function where it will be hashed for 15 seconds (default) together with the salt generated during encryption.
    A 16-byte counter needed for the AES algorithm in CTR mode is also generated.
    When decrypting the ciphertext, the HMAC is also calculated and compared with the HMAC received from the recipient, in order to verify it.
    If the password is correct, the decrypted message and the HMAC validity are returned. Otherwise, an exception is thrown and None is returned.

    Args:
        password (str): Answer given by the recipient to the question imposed by the sender to decrypt the ciphertext.
        input (list[str]): List containing the number of hashing iterations, the salt, the ciphertext, the HMAC calculated and the digital signature of the ciphertext.

    Returns:
        tuple[bytes, bool]: A tuple containing the decrypted message and the HMAC validity.
    """
    iter_counter: int = int(input[0])
    salt: bytes = bytes.fromhex(input[2])
    ciphertext: bytes = bytes.fromhex(input[3])[HMAC_SIZE:]

    counter = Counter.new(nbits=BLOCK_SIZE*8)
    key: bytes = hf.find_hash(iter_counter, salt, password)
    cipher = AES.new(key, AES.MODE_CTR, counter=counter)

    decrypted_msg: bytes = cipher.decrypt(ciphertext)

    try:
        decrypted_msg: str = decrypted_msg.decode()
        hmac_received: str = input[3][:HMAC_SIZE]
        hmac_value: str = mf.calculate_hmac(ciphertext, password)[:HMAC_SIZE]

        # Debugging
        print(f"HMAC R: {hmac_received}")
        print(f"HMAC C: {hmac_value}")

        hmac_validity: bool = (hmac_received == hmac_value)

        return decrypted_msg, hmac_validity
    except:
        print("Decryption failed. Wrong password.")
        
        return None, None

