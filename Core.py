from Init import *
import hashlib
import string
import random
from mysql.connector import errorcode


class Header:
    Login = "Login"
    Split = "||"


def Read(Client, BufferSize):
    Buffer = ""
    Size = None
    Request = "Init"
    while len(Request):
        Request = Client.recv(BufferSize).decode()
        Buffer += Request
        if Size is None:
            Size, Buffer = Buffer.split(Header.Split, maxsplit=1)
            Size = int(Size)
        if Size - len(Buffer) <= 0:
            return Buffer
    return Buffer


def TableExist(name):
    Core.Cursor.execute("SHOW TABLES")
    for x in Core.Cursor:
        if x[0] == name:
            return True
    return False


def InitUserDatabase():
    if not TableExist("Credentials"):
        Core.Cursor.execute("CREATE TABLE Credentials (Username VARCHAR(128) PRIMARY KEY, Password VARCHAR(128), "
                            "ID VARCHAR(512) UNIQUE )")


def InitBookDatabase():
    if not TableExist("Books"):
        Core.Cursor.execute(
            "CREATE TABLE Books (ISBN VARCHAR(512) PRIMARY KEY ,BookName VARCHAR(512) ,Author VARCHAR(512) ,"
            "Availability INTEGER);")


def CreateUser(Username: str, Password: str):
    ID = hashlib.sha512(f"{Username}-"
                        f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}".encode()).hexdigest()
    try:
        Core.Cursor.execute(f"INSERT INTO Credentials(Username , Password, ID) VALUES (%s, %s,%s)",
                            (Username, Password, ID))
        Core.Database.commit()
    except mysql.connector.Error as Error:
        pass


def RemoveUser(Username: str):
    Core.Cursor.execute("DELETE FROM Credentials WHERE Username =  %s ", (Username,))
    Core.Database.commit()


def IsUser(Username: str):
    Core.Cursor.execute("SELECT COUNT(*) FROM Credentials WHERE Username = %s", (Username,))
    if Core.Cursor.fetchone()[0] == 1:
        return True
    return False


def GetLatest(self):
    pass


def GetDigital(self, Books: str):
    pass


Core = Init("192.168.1.6")
