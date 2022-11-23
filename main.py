from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode

key = get_random_bytes(16)

cipher = AES.new(key, AES.MODE_EAX) #TODO: find out what eax means
tag = '' #TODO: find out what tag means / is for and if it'll break anything


ENCRYPT_TAG = ' e('
CLOSING_TAG = ')d '

# text: text to check for encrypt or decrypt
# encrypt: tell whether to encrypt or decrypt what's inside the value
def findEncryptValue(text, encrypt=True):
    beginPos = text.rfind(ENCRYPT_TAG)
    endPos = text.rfind(CLOSING_TAG)

    do_stuff = text[beginPos+len(ENCRYPT_TAG):endPos]
    print(f'do_stuff: {do_stuff}')
    fancy_text = ''

    # TODO: find all e() that could be if we do multiple. Not super important
    if encrypt:
        fancy_text = encryptText(do_stuff)
    else:
        fancy_text = decryptText(do_stuff)

    text = text.replace(do_stuff, fancy_text)

    print(f'ciphertext: {fancy_text}')
    print(f'encrypted: {text}')

    return text 

def encryptText(plaintext):
    ciphertext, tag = cipher.encrypt_and_digest(bytes(plaintext, 'utf-8'))
    return b64encode(ciphertext).decode( 'utf-8' )

def decryptText(ciphertext):
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data.decode('UTF-8')


# def search(searchQuery, row, table):


encrypted_value = findEncryptValue(f'something important: {ENCRYPT_TAG}encrypt me{CLOSING_TAG}')



print(findEncryptValue(encrypted_value, False))