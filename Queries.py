from Init import *
import hashlib
import string
import random
from newsapi import NewsApiClient
from datetime import datetime, timedelta


# Constants
class Privileges:
    SuperAdmin = 1
    Admin = 2
    User = 4


class Type:
    Online = 1
    Offline = 2


Core = Init("10.0.0.6")
NewsAPIClientKey = "9d61afd84fd840efafd110ab7e4fd55f"
UpdateTime = None
Headlines = ""
TargetedHeadlines = {"business": "",
                     "entertainment": "",
                     "general": "",
                     "health": "",
                     "science": "",
                     "sports": "",
                     "technology": ""}
TargetedHeadlinesUpdateTime = {"business": None,
                               "entertainment": None,
                               "general": None,
                               "health": None,
                               "science": None,
                               "sports": None,
                               "technology": None}


# Supporting queries
def TableExist(Name: str):
    Core.Cursor.execute("SHOW TABLES;")
    for x in Core.Cursor:
        if x[0] == Name:
            return True
    return False


def DeleteTable(Name: str):
    if TableExist(Name):
        Core.Cursor.execute(f"DROP TABLE {Name};")
        return True
    return False


# User login queries
def InitUserTable():
    if not TableExist("Credentials"):
        Core.Cursor.execute("CREATE TABLE Credentials (Username VARCHAR(128) PRIMARY KEY, Password VARCHAR(128), "
                            "ID VARCHAR(512) UNIQUE , Privilege INT);")
        return True
    return False


def AddUser(Username: str, Password: str, Permission: int):
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
        return True
    except mysql.connector.Error as Error:
        return False


def UpdateUser(Username: str, Password: str, Permission: int):
    if AddUser(Username, Password, Permission):
        return True
    else:
        if RemoveUser(Username) and AddUser(Username, Password, Permission):
            return True
        return False


def IsUser(Username: str):
    Core.Cursor.execute("SELECT COUNT(*) FROM Credentials WHERE Username = %s;", (Username,))
    if Core.Cursor.fetchone()[0] == 1:
        return True
    return False


def AuthUser(Username: str, Password: str):
    try:
        Core.Cursor.execute("SELECT ID FROM Credentials WHERE Username = %s and Password = %s;", (Username, Password))
        return Core.Cursor.fetchone()[0]
    except mysql.connector.Error as Error:
        return None


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


# Books related queries
def InitBookDatabase():
    if not TableExist("BooksRecord"):
        try:
            Core.Cursor.execute(
                "CREATE TABLE BooksRecord (ISBN VARCHAR(512) PRIMARY KEY ,BookName VARCHAR(512) ,Author VARCHAR(512) ,"
                "Availability INTEGER , TYPE INTEGER );")
            return True
        except mysql.connector.Error as Error:
            return False
    return False


def AddBookRecord(Name: str, ISBN: str, Author: str, Availability: int, Type: int):
    try:
        Core.Cursor.execute(
            "INSERT INTO BooksRecord(BookName,ISBN,Author,Availability,TYPE ) VALUES (%s, %s,%s,%s,%s);",
            (Name, ISBN, Author, Availability, Type))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


def UpdateBookRecord(Name: str, ISBN: str, Author: str, Availability: int, Type: int):
    if AddBookRecord(Name, ISBN, Author, Availability, Type):
        return True
    else:
        if RemoveBookRecord(ISBN) and AddBookRecord(Name, ISBN, Author, Availability, Type):
            return True
        return False


def RemoveBookRecord(ISBN: str):
    try:
        Core.Cursor.execute("DELETE FROM BooksRecord WHERE ISBN = %s;", (ISBN,))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


"""
Searches 
param Key: [Name, ISBN, Author]
return First N values in [BookName,ISBN,Author,Availability,TYPE] this order
"""


def SearchBookName(Name: str, N: int):
    Core.Cursor.execute("SELECT BookName,ISBN,Author,Availability,TYPE  FROM BooksRecord WHERE BookName like %s;",
                        (Name + "%",))
    return Core.Cursor.fetchmany(N)


def SearchISBN(ISBN: str, N: int):
    Core.Cursor.execute("SELECT BookName,ISBN,Author,Availability,TYPE  FROM BooksRecord WHERE ISBN like %s;",
                        (ISBN + "%",))
    return Core.Cursor.fetchmany(N)


def SearchAuthor(Author: str, N: int):
    Core.Cursor.execute("SELECT BookName,ISBN,Author,Availability,TYPE  FROM BooksRecord WHERE Author like %s;",
                        (Author + "%",))
    return Core.Cursor.fetchmany(N)


# Digital books related queries
def InitDigitalBookTable():
    if not TableExist("DigitalBooks"):
        Core.Cursor.execute("CREATE TABLE DigitalBooks (ISBN VARCHAR(512) PRIMARY KEY , Location VARCHAR(4096) );")


def AddDigital(ISBN: str, Location: str):
    try:
        Core.Cursor.execute("INSERT INTO DigitalBooks (ISBN , Location) VALUES (%s,%s);", (ISBN, Location))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


def RemoveDigital(ISBN: str):
    try:
        Core.Cursor.execute("DELETE FROM DigitalBooks WHERE ISBN =  %s ;", (ISBN,))
        Core.Database.commit()
        return True
    except mysql.connector.Error as Error:
        return False


def UpdateDigital(ISBN: str, Location: str):
    if AddDigital(ISBN, Location):
        return True
    else:
        if RemoveDigital(ISBN) and AddDigital(ISBN, Location):
            return True
        return False


def GetDigital(ISBN: str):
    Core.Cursor.execute("SELECT Location FROM DigitalBooks WHERE ISBN = %s;", (ISBN,))
    return Core.Cursor.fetchone()[0]


# Update headlines
def UpdateLatestNews():
    global UpdateTime, Headlines
    newsapi = NewsApiClient(api_key=NewsAPIClientKey)
    if UpdateTime is None or UpdateTime - datetime.now() > timedelta(minutes=30):
        Headlines = newsapi.get_top_headlines()
        if Headlines["status"] == "ok":
            UpdateTime = datetime.now()
            return True
        else:
            return False
    return True


def UpdateAllLatestNewsCategory():
    global TargetedHeadlines, TargetedHeadlinesUpdateTime
    newsapi = NewsApiClient(api_key=NewsAPIClientKey)
    for key in TargetedHeadlines.keys():
        if TargetedHeadlinesUpdateTime[key] is None or TargetedHeadlinesUpdateTime[key] - datetime.now() > timedelta(
                minutes=30):
            Data = newsapi.get_top_headlines(category=key)
            if Data["status"] == "ok":
                TargetedHeadlinesUpdateTime[key] = datetime.now()
                TargetedHeadlines[key] = Data


def UpdateLatestNewsCategory(Category: str):
    global TargetedHeadlines, TargetedHeadlinesUpdateTime
    newsapi = NewsApiClient(api_key=NewsAPIClientKey)
    if TargetedHeadlinesUpdateTime[Category] is None or\
            TargetedHeadlinesUpdateTime[Category] - datetime.now() > timedelta(minutes=30):
        Data = newsapi.get_top_headlines(category=Category)
        if Data["status"] == "ok":
            TargetedHeadlinesUpdateTime[Category] = datetime.now()
            TargetedHeadlines[Category] = Data


def GetNewsCategory(Category: str):
    UpdateLatestNewsCategory(Category)
    return TargetedHeadlines[Category]


def GetLatestNewCategory():
    UpdateLatestNews()
    return Headlines
