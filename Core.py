from Init import *
import hashlib
import string
import random
from mysql.connector import errorcode


class Header:
    Login = "Login"
    Split = "||"


class Privileges:
    SuperAdmin = 1
    Admin = 2
    User = 4


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


def TableExist(Name: str):
    Core.Cursor.execute("SHOW TABLES;")
    for x in Core.Cursor:
        if x[0] == Name:
            return True
    return False


def InitUserTable():
    if not TableExist("Credentials"):
        Core.Cursor.execute("CREATE TABLE Credentials (Username VARCHAR(128) PRIMARY KEY, Password VARCHAR(128), "
                            "ID VARCHAR(512) UNIQUE , Privilege INT);")
        return True
    return False


def DeleteTable(Name: str):
    if TableExist(Name):
        Core.Cursor.execute(f"DROP TABLE {Name};")
        return True
    return False


def InitBookDatabase():
    if not TableExist("Books"):
        Core.Cursor.execute(
            "CREATE TABLE BooksRecord (ISBN VARCHAR(512) PRIMARY KEY ,BookName VARCHAR(512) ,Author VARCHAR(512) ,"
            "Availability INTEGER);")


def CreateUser(Username: str, Password: str, Permission: int):
    ID = hashlib.sha512(f"{Username}-"
                        f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}".encode()).hexdigest()
    try:
        Core.Cursor.execute("INSERT INTO Credentials(Username , Password, ID, Privilege) VALUES (%s, %s,%s,%s);",
                            (Username, Password, ID, Permission))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


def RemoveUser(Username: str):
    try:
        Core.Cursor.execute("DELETE FROM Credentials WHERE Username =  %s ;", (Username,))
        Core.Database.commit()
    except mysql.connector.Error as Error:
        return False


def IsUser(Username: str):
    Core.Cursor.execute("SELECT COUNT(*) FROM Credentials WHERE Username = %s;", (Username,))
    if Core.Cursor.fetchone()[0] == 1:
        return True
    return False


def GetPrivilege(Username: str):
    try:
        Core.Cursor.execute("SELECT Privilege FROM Credentials WHERE Username = %s;", (Username,))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return -1
        else:
            return Data[0]
    except mysql.connector.Error as Error:
        return -1


def AddBookRecord(Name: str, ISBN: str, Author: str, Availability: int):
    try:
        Core.Cursor.execute("INSERT INTO BooksRecord(BookName,ISBN,Author,Availability) VALUES (%s, %s,%s,%s);",
                            (Name, ISBN, Author, Availability))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


def UpdateBookRecord(Name: str, ISBN: str, Author: str, Availability: int):
    try:
        Core.Cursor.execute("INSERT INTO BooksRecord(BookName,ISBN,Author,Availability) VALUES (%s, %s,%s,%s);",
                            (Name, ISBN, Author, Availability))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        Core.Cursor.execute("DELETE FROM BooksRecord WHERE BookName = %s;", (Name,))
        Core.Database.commit()
        try:
            Core.Cursor.execute("INSERT INTO BooksRecord(BookName,ISBN,Author,Availability) VALUES (%s, %s,%s,%s);",
                                (Name, ISBN, Author, Availability))
            Core.Database.commit()
            return True
        except mysql.connector.Error as Error:
            return False


def RemoveBookRecord(Name: str):
    try:
        Core.Cursor.execute("DELETE FROM BooksRecord WHERE BookName = %s;", (Name,))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


def GetLatest(self):
    pass


def GetDigital(self, Books: str):
    pass


Core = Init("192.168.1.6")
