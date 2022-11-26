from Crypto.Cipher import AES
from Crypto import Random
import base64
import sqlite3

random = Random.new()

# KEY AND IV WILL BE DIFFERENT EVERY TIME THE PROGRAM IS RAN
key = random.read(AES.key_size[0])
iv = random.read(AES.block_size)


BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

conn = sqlite3.connect('cloud.db')


ENCRYPT_TAG = 'e('
CLOSING_TAG = ')d'


# encrypt: tell whether to encrypt or decrypt what's inside the value
def findEncryptValue(text, encrypt=True):
    beginPos = text.rfind(ENCRYPT_TAG)
    endPos = text.rfind(CLOSING_TAG)

    if (beginPos == endPos):
        return text

    do_stuff = text[beginPos+len(ENCRYPT_TAG):endPos]
    fancy_text = ''

    # TODO: find all e() that could be if we do multiple. Not super important
    if encrypt:
        fancy_text = encryptText(do_stuff)
    else:
        fancy_text = decryptText(do_stuff)

    text = text.replace(do_stuff, fancy_text)


    return text 

def encryptText(plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = pad(plaintext)
    return base64.b64encode(cipher.encrypt(plaintext)).decode()

def decryptText(ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)

    decoded = base64.b64decode(ciphertext)
    
    data = unpad(cipher.decrypt(decoded))
    return bytes.decode(data)

def getTable():
    while True:
        print('TABLES IN DATABASE')
        res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = []
        for name in res.fetchall():
            print(name[0])
            tables.append(name[0])

        tableQuery = input('Which Table would you like to use? (please type in full name): ')
        if tableQuery in tables:
            return tableQuery
        else:
            print("I'm sorry, that is not a valid table")

def getColumns(selectedTable):
    res = conn.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{selectedTable}');")
    columns = []

    for name in res.fetchall():
        columns.append(name[0])

    return columns

def search():
    # Get table
    selectedTable = getTable()
    

    # Get columns
    print("Here's the list of columns available: ")

    for column in getColumns(selectedTable):
        print(column)

    exactSearch = input('Is this an exact search? (y/n): ')

    if exactSearch.lower() == 'y':
        query = input('Please place in the exact column and query to do an exact search (ID=\'x\'): ')
        query = findEncryptValue(query)
        res = conn.execute(f"SELECT * from {selectedTable} WHERE {query};")

        print("results: ")
        for result in res.fetchall():
            row = ''
            for col in result:
                row += ' | ' + findEncryptValue(str(col), False) + ' | '

        print(row)
    else:
        colQuery = input('What column would you like to search?: ')
        searchQuery = input('What value would you like to search (encrypted values will not be searched): ')

        print('Query: ' + f"SELECT * from {selectedTable} WHERE {colQuery} like '%{searchQuery}%';")

        res = conn.execute(f"SELECT * from {selectedTable} WHERE {colQuery} like '%{searchQuery}%';")

        print("results: ")
        for result in res.fetchall():
            row = ''
            for col in result:
                row += ' | ' + findEncryptValue(str(col), False) + ' | '
            print(row)

def createRow():
    table = getTable()

    print(f"Let's create a row in the database!\nRemember to use {ENCRYPT_TAG} <data> {CLOSING_TAG} to encrypt what you want!\n")

    columns = getColumns(table)

    columnList = '('
    for column in columns:
        if column == "ID":
            continue
        columnList += column + ', '
    columnList = columnList[:len(columnList) - 2] + ')'
    print("Here's the columns you have to fill!")

    print(columnList)

    dataInput = '('
    for column in columns:
        if column == "ID":
            continue
        data = input(f"What do you want to place in {column}: ")
        dataInput += "'" + findEncryptValue(data) + "', "
    
    dataInput = dataInput[:len(dataInput) - 2] + ')'


    res = conn.execute(f"INSERT INTO {table} {columnList} VALUES {dataInput}")
    conn.commit()
    print("Records successfully inserted")


def main():
    while True:
        print('\nHello! Welcome to the Cloud Banking Database! What would you like to do?\n')
        print('1: search database')
        print('2: create row in database')
        print('3: update row in database')
        print("Press 'q' to quit!")

        customerPick = input()

        if (customerPick == '1'):
            search()
        if (customerPick == '2'):
            createRow()
        if (customerPick == 'q'):
            return
    
        

main()
conn.close()