import json

from Init import Init
import hashlib
import string
import random
import mysql.connector
from newsapi.newsapi_client import NewsApiClient
from datetime import datetime, timedelta
from Constants import *

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
def TableExist(Core: Init, Name: str):
    Core.Cursor.execute("SHOW TABLES;")
    for x in Core.Cursor:
        if x[0] == Name:
            return True
    return False


def DeleteTable(Core: Init, Name: str):
    if TableExist(Core, Name):
        Core.Cursor.execute(f"DROP TABLE {Name};")
        return True
    return False


# User login queries
def InitUserTable(Core: Init):
    if not TableExist(Core, "credentials"):
        Core.Cursor.execute("CREATE TABLE Credentials (Username VARCHAR(128) PRIMARY KEY, Password VARCHAR(128), "
                            "ID VARCHAR(512) UNIQUE , Privilege INT);")
        return True
    return False


def AddUser(Core: Init, Username: str, Password: str, Permission: int):
    ID = hashlib.sha512(f"{Username}-"
                        f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}".encode()).hexdigest()
    try:
        Core.Cursor.execute("INSERT INTO Credentials(Username , Password, ID, Privilege) VALUES (%s, %s,%s,%s);",
                            (Username, Password, ID, Permission))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def RemoveUser(Core: Init, Username: str):
    try:
        Core.Cursor.execute("DELETE FROM Credentials WHERE Username =  %s ;", (Username,))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def UpdateUser(Core: Init, Username: str, Password: str, Permission: int):
    if AddUser(Core, Username, Password, Permission):
        return True
    else:
        if RemoveUser(Core, Username) and AddUser(Core, Username, Password, Permission):
            return True
        return False


def IsUserUsername(Core: Init, Username: str):
    Core.Cursor.execute("SELECT COUNT(*) FROM Credentials WHERE Username = %s;", (Username,))
    if Core.Cursor.fetchone()[0] == 1:
        return True
    return False


def IsUserID(Core: Init, ID: str):
    Core.Cursor.execute("SELECT COUNT(*) FROM Credentials WHERE ID = %s;", (ID,))
    if Core.Cursor.fetchone()[0] == 1:
        return True
    return False


def AuthUser(Core: Init, Username: str, Password: str):
    try:
        Core.Cursor.execute("SELECT ID FROM Credentials WHERE Username = %s and Password = %s;", (Username, Password))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return None
        else:
            return Data[0]
    except mysql.connector.Error:
        return None


def GetPrivilegeByUsername(Core: Init, Username: str):
    try:
        Core.Cursor.execute("SELECT Privilege FROM Credentials WHERE Username = %s;", (Username,))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return -2
        else:
            return Data[0]
    except mysql.connector.Error:
        return -1


def GetPasswordByUsername(Core: Init, Username: str):
    try:
        Core.Cursor.execute("SELECT Password FROM Credentials WHERE Username = %s;", (Username,))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return -2
        else:
            return Data[0]
    except mysql.connector.Error:
        return -1


def GetPrivilegeByID(Core: Init, ID: str):
    try:
        Core.Cursor.execute("SELECT Privilege FROM Credentials WHERE ID = %s;", (ID,))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return -2
        else:
            return Data[0]
    except mysql.connector.Error:
        return -1


def GetPasswordByID(Core: Init, ID: str):
    try:
        Core.Cursor.execute("SELECT Password FROM Credentials WHERE ID = %s;", (ID,))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return -2
        else:
            return Data[0]
    except mysql.connector.Error:
        return -1


def GetUsername(Core: Init, ID: str):
    try:
        Core.Cursor.execute("SELECT Username FROM Credentials WHERE ID = %s;", (ID,))
        Data = Core.Cursor.fetchone()
        if Data is None:
            return -2
        else:
            return Data[0]
    except mysql.connector.Error:
        return -1


# Books related queries
def InitBookDatabase(Core: Init):
    if not TableExist(Core, "booksrecord"):
        try:
            Core.Cursor.execute(
                "CREATE TABLE BooksRecord (ISBN VARCHAR(512) PRIMARY KEY ,BookName VARCHAR(512),Thumbnail VARCHAR(4096)"
                ",Author VARCHAR(512) ,Availability INTEGER , Type INTEGER );")
            return True
        except mysql.connector.Error:
            return False
    return False


def AddBookRecord(Core: Init, Name: str, ISBN: str, Author: str, Availability: int, Type: int, Thumbnail: str):
    try:
        Core.Cursor.execute(
            "INSERT INTO BooksRecord(BookName,ISBN,Thumbnail,Author,Availability,Type) VALUES (%s, %s,%s,%s,%s,%s);",
            (Name, ISBN, Thumbnail, Author, Availability, Type))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def UpdateBookRecord(Core: Init, Name: str, ISBN: str, Author: str, Availability: int, Type: int, Thumbnail: str):
    if AddBookRecord(Core, Name, ISBN, Author, Availability, Type, Thumbnail):
        return True
    else:
        if RemoveBookRecord(Core, ISBN) and AddBookRecord(Core, Name, ISBN, Author, Availability, Type, Thumbnail):
            return True
        return False


def RemoveBookRecord(Core: Init, ISBN: str):
    try:
        Core.Cursor.execute("DELETE FROM BooksRecord WHERE ISBN = %s;", (ISBN,))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


"""
Searches 
param Key: [Name, ISBN, Author]
return First N values in [BookName,ISBN,Thumbnail,Author,Availability,Type] this order
"""


def SearchBookName(Core: Init, Name: str, N: int):
    Core.Cursor.execute("SELECT BookName,ISBN,Thumbnail,Author,Availability,Type  FROM BooksRecord WHERE BookName "
                        "like %s;", (Name + "%",))
    return Core.Cursor.fetchmany(N)


def SearchISBN(Core: Init, ISBN: str, N: int):
    Core.Cursor.execute("SELECT BookName,ISBN,Thumbnail,Author,Availability,Type  FROM BooksRecord WHERE ISBN like %s;",
                        (ISBN + "%",))
    return Core.Cursor.fetchmany(N)


def SearchAuthor(Core: Init, Author: str, N: int):
    Core.Cursor.execute(
        "SELECT BookName,ISBN,Thumbnail,Author,Availability,Type FROM BooksRecord WHERE Author like %s;",
        (Author + "%",))
    return Core.Cursor.fetchmany(N)


# Digital books related queries
def InitDigitalBookTable(Core: Init):
    if not TableExist(Core, "digitalbooks"):
        Core.Cursor.execute("CREATE TABLE DigitalBooks (ISBN VARCHAR(512) PRIMARY KEY , Location VARCHAR(4096) );")


def AddDigital(Core: Init, ISBN: str, Location: str):
    try:
        Core.Cursor.execute("INSERT INTO DigitalBooks (ISBN , Location) VALUES (%s,%s);", (ISBN, Location))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def RemoveDigital(Core: Init, ISBN: str):
    try:
        Core.Cursor.execute("DELETE FROM DigitalBooks WHERE ISBN =  %s ;", (ISBN,))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def UpdateDigital(Core: Init, ISBN: str, Location: str):
    if AddDigital(Core, ISBN, Location):
        return True
    else:
        if RemoveDigital(Core, ISBN) and AddDigital(Core, ISBN, Location):
            return True
        return False


def GetDigital(Core: Init, ISBN: str):
    try:
        Core.Cursor.execute("SELECT Location FROM DigitalBooks WHERE ISBN = %s;", (ISBN,))
        Data = Core.Cursor.fetchone()[0]
        if Data is None:
            return -2
        else:
            return Data[0]
    except mysql.connector.Error:
        return -1


# Update headlines
def UpdateLatestNews():
    def Parser(Strings: list):
        print(Strings)
        Data = Header.Split.join(Strings)
        return f"{len(Data)}{Header.Split}{Data}".encode()

    global UpdateTime, Headlines
    newsapi = NewsApiClient(api_key=NewsAPIClientKey)
    if UpdateTime is None or UpdateTime - datetime.now() > timedelta(minutes=30):
        Headlines = newsapi.get_top_headlines(language='en', page_size=100)
        if Headlines["status"] == "ok":
            Headlines = json.dumps(Headlines)
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
            Data = newsapi.get_top_headlines(category=key, language='en', page_size=100)
            if Data["status"] == "ok":
                TargetedHeadlinesUpdateTime[key] = datetime.now()
                TargetedHeadlines[key] = json.dumps(Data)


def UpdateLatestNewsCategory(Category: str):
    global TargetedHeadlines, TargetedHeadlinesUpdateTime
    newsapi = NewsApiClient(api_key=NewsAPIClientKey)
    if TargetedHeadlinesUpdateTime[Category] is None or \
            TargetedHeadlinesUpdateTime[Category] - datetime.now() > timedelta(minutes=30):
        Data = newsapi.get_top_headlines(category=Category, language='en', page_size=100)
        if Data["status"] == "ok":
            TargetedHeadlinesUpdateTime[Category] = datetime.now()
            TargetedHeadlines[Category] = json.dumps(Data)


def GetLatestNewsCategory(Category: str):
    UpdateLatestNewsCategory(Category)
    return TargetedHeadlines[Category]


def GetLatestNewsCategoryUpdateTime(Category: str):
    return TargetedHeadlinesUpdateTime[Category].strftime("%m/%d/%Y, %H:%M:%S")


def GetLatestNews():
    UpdateLatestNews()
    return Headlines


def GetLatestNewsUpdateTime():
    return UpdateTime.strftime("%m/%d/%Y, %H:%M")


# Acquisition

def InitBookRequests(Core: Init):
    if not TableExist(Core, "requestsrecord"):
        try:
            Core.Cursor.execute(
                "CREATE TABLE RequestsRecord (RQNO VARCHAR(512) PRIMARY KEY ,BookName VARCHAR(512) ,Author VARCHAR("
                "512) ,RequestedBy VARCHAR(512) , Status VARCHAR(512) );")
            return True
        except mysql.connector.Error:
            return False
    return False


def CreateNewRequest(Core: Init, Name: str, Author: str, RequestedBy: str, Status=RequestStatus.processing):
    try:
        rqno = int(GetLastRecord(Core)) + 1
        Core.Cursor.execute(
            "INSERT INTO RequestsRecord(BookName,RQNO,Author,RequestedBY,Status ) VALUES (%s, %s,%s,%s,%s);",
            (Name, rqno, Author, RequestedBy, Status))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def GetLastRecord(Core: Init):
    Core.Cursor.execute("Select Max(RQNO) from RequestsRecord")
    return Core.Cursor.fetchone()


def UpdateRequestStatus(Core: Init, Status: RequestStatus, RQNO: int):
    try:
        Core.Cursor.execute("UPDATE RequestsRecord SET Status = %s where RQNO = %s", (Status, RQNO))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def GetPendingRequests(Core: Init):
    Core.Cursor.execute("Select * from RequestsRecord where Status = %s", (RequestStatus.processing,))
    return Core.Cursor.fetchall()


def CheckBookIfExist(Core: Init, BookName: str):
    Core.Cursor.execute("SELECT *  FROM BooksRecord WHERE BookName like %s;",
                        (BookName + "%",))
    st = Core.Cursor.fetchmany()
    if len(st) == 0:
        return False
    else:
        return True
