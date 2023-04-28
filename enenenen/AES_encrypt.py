import base64
from Crypto.Cipher import AES
import hashlib

iv = '1234567890123456'

# 设置加密参数
BS = 16
# pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
pad = lambda s: s + (BS - len(s) % BS) * bytes([BS - len(s) % BS])
# unpad = lambda s : s[0:-ord(s[-1])]

unpad = lambda s : s[0:-s[-1] if isinstance(s[-1], int) else ord(s[-1])]
# key = b'This is a secret key'
# iv = b'This is an IV456'

# 定义加密函数
def encrypt(message, key):
    message = pad(message.encode('utf-8'))
    cipher = AES.new(hashlib.sha256(key.encode('utf-8')).digest(), AES.MODE_CBC, iv.encode('utf-8'))
    ciphertext = cipher.encrypt(message)
    return base64.b64encode(ciphertext).decode()
# 定义解密函数
def decrypt(ciphertext, key):
    ciphertext = base64.b64decode(ciphertext)
    cipher = AES.new(hashlib.sha256(key.encode('utf-8')).digest(), AES.MODE_CBC, iv.encode('utf-8'))
    decrypted_text = unpad(cipher.decrypt(ciphertext))
    return decrypted_text.decode()
# 对明文进行加密
def aes_encrypt(data, key):
    key = hashlib.sha256(key.encode('utf-8')).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv.encode('utf-8'))
    data = data.encode('utf-8')
    data = data + b"\0" * (AES.block_size - len(data) % AES.block_size)
    ciphertext = cipher.encrypt(data)
    return base64.b64encode(ciphertext).decode()

# 对密文进行解密
def aes_decrypt(data, key):
    key = hashlib.sha256(key.encode('utf-8')).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv.encode('utf-8'))
    ciphertext = base64.b64decode(data)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.rstrip(b"\0").decode('utf-8')

# 测试加密和解密函数
username = '张三'
id = 411502211126990336
key ='mysecretpassword'
encrypted_username = aes_encrypt(username, key)
print('Encrypted username:', encrypted_username)
decrypted_username = aes_decrypt(encrypted_username, key)
print('Decrypted username:', decrypted_username)
# key = b'mysecretpassword'

id_number = '415502199926261133'
encrypted_id = encrypt(id_number,key)
print('Encrypted ID number:', encrypted_id)
decrypted_id = decrypt(encrypted_id, key)
print('Decrypted ID number:', decrypted_id)