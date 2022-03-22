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
    if not TableExist(Core, "Credentials"):
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
    if not TableExist(Core, "BooksRecord"):
        Core.Cursor.execute(
            "CREATE TABLE BooksRecord (ISBN VARCHAR(512) PRIMARY KEY ,BookName VARCHAR(512),Thumbnail VARCHAR(4096)"
            ",Author VARCHAR(512) ,Availability INTEGER , Type INTEGER );")
        return True
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


def SearchBookName(Core: Init, Name: str, N: int, Sort="ASC"):
    Core.Cursor.execute("SELECT BookName,ISBN,Thumbnail,Author,Availability,Type  FROM BooksRecord WHERE BookName "
                        f"like %s ORDER  BY ISBN {Sort};", (Name + "%",))
    return Core.Cursor.fetchmany(N)


def SearchISBN(Core: Init, ISBN: str, N: int, Sort="ASC"):
    Core.Cursor.execute("SELECT BookName,ISBN,Thumbnail,Author,Availability,Type  FROM BooksRecord WHERE ISBN like %s "
                        f"ORDER  BY ISBN {Sort};",
                        (ISBN + "%", ))
    return Core.Cursor.fetchmany(N)


def SearchAuthor(Core: Init, Author: str, N: int, Sort="ASC"):
    Core.Cursor.execute("SELECT BookName,ISBN,Thumbnail,Author,Availability,Type FROM BooksRecord WHERE Author like "
                        "%s ORDER  BY ISBN %s;",
                        (Author + "%", Sort))
    return Core.Cursor.fetchmany(N)


# Digital books related queries
def InitDigitalBookTable(Core: Init):
    if not TableExist(Core, "DigitalBooks"):
        Core.Cursor.execute("CREATE TABLE DigitalBooks (ISBN VARCHAR(512) NOT NULL, Location VARCHAR(4096) ,"
                            "FOREIGN KEY (ISBN) REFERENCES BooksRecord(ISBN));")
        return True
    return False


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
    if not TableExist(Core, "RequestsRecord"):
        Core.Cursor.execute("CREATE TABLE RequestsRecord (ReqNO INT(255) AUTO_INCREMENT PRIMARY KEY ,BookName VARCHAR("
                            "512) ,Author VARCHAR(512) ,RequestedBy VARCHAR(512) , Status VARCHAR(512) "
                            ",FOREIGN KEY (RequestedBy) REFERENCES Credentials (Username));")
        return True
    return False


def RequestBooks(Core: Init, Name: str, Author: str, RequestedBy: str, Status=RequestStatus.processing):
    try:
        Core.Cursor.execute(
            "INSERT INTO RequestsRecord(BookName,Author,RequestedBY,Status ) VALUES (%s,%s,%s,%s);",
            (Name, Author, RequestedBy, Status))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def GetBookRequestCount(Core: Init):
    Core.Cursor.execute("Select Max(ReqNO) from RequestsRecord")
    return Core.Cursor.fetchone()


def UpdateBookRequestStatus(Core: Init, Status: RequestStatus, ReqNo: int):
    try:
        Core.Cursor.execute("UPDATE RequestsRecord SET Status = %s where ReqNO = %s", (Status, ReqNo))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def GetBookRequests(Core: Init):
    Core.Cursor.execute("Select * from RequestsRecord; ")
    return Core.Cursor.fetchall()


def GetBookRequestsByStatus(Core: Init, Status):
    Core.Cursor.execute("Select * from RequestsRecord where Status = %s", (Status,))
    return Core.Cursor.fetchall()


def GetBookRequestsByUserName(Core: Init, Name: str):
    Core.Cursor.execute("Select * from RequestsRecord where RequestedBy = %s", (Name,))
    return Core.Cursor.fetchall()


def GetBookRequestsByUserNameAndStatus(Core: Init, Name: str, Status):
    Core.Cursor.execute("Select * from RequestsRecord where RequestedBy = %s AND Status = %s", (Name, Status))
    return Core.Cursor.fetchall()


# Serial Control


def InitMagazines(Core: Init):
    if not TableExist(Core, "Magazines"):
        Core.Cursor.execute("CREATE TABLE Magazines (JournalName VARCHAR(512) PRIMARY KEY );")
        return True
    return False


def InitMagazineRecord(Core: Init):
    if not TableExist(Core, "MagazineRecord"):
        Core.Cursor.execute("CREATE TABLE MagazineRecord (JournalName VARCHAR(512) ,Volume VARCHAR(128),"
                            "Issue VARCHAR(128),ReleaseDate DATE, Location VARCHAR(4096), FOREIGN KEY (JournalName)"
                            " REFERENCES Magazines(JournalName));")
        return True
    return False


def InitMagazineAuthorRecord(Core: Init):
    if not TableExist(Core, "MagazineAuthorRecord"):
        Core.Cursor.execute("CREATE TABLE MagazineAuthorRecord (JournalName VARCHAR(512),ReleaseDate DATE,"
                            "Author VARCHAR(512), FOREIGN KEY (JournalName) REFERENCES Magazines(JournalName));")
        return True
    return False


def InitStudentMagazineRecord(Core: Init):
    if not TableExist(Core, "StudentMagazineRecord"):
        Core.Cursor.execute("CREATE TABLE StudentMagazineRecord (UserName VARCHAR(512), JournalName VARCHAR(512), "
                            "Email VARCHAR(512), FOREIGN KEY (JournalName) REFERENCES Magazines(JournalName),"
                            "FOREIGN KEY (UserName) REFERENCES Credentials(UserName));")
        return True
    return False


def InitStudentMagazineRequestRecord(Core: Init):
    if not TableExist(Core, "StudentMagazineRequestRecord"):
        Core.Cursor.execute("CREATE TABLE StudentMagazineRequestRecord (ReqNO INT(255) AUTO_INCREMENT PRIMARY KEY ,"
                            "UserName VARCHAR(512), JournalName VARCHAR(512),Status INTEGER (255),Email VARCHAR(512),"
                            " FOREIGN KEY (JournalName) REFERENCES Magazines(JournalName),"
                            "FOREIGN KEY (UserName) REFERENCES Credentials(UserName));")
        return True
    return False


def GetMagazineByUserName(Core: Init, UserName: str):
    Core.Cursor.execute("Select JournalName from StudentMagazineRecord WHERE UserName = %s; ", (UserName,))
    return Core.Cursor.fetchall()


def GetMagazineCountByUserName(Core: Init, UserName: str):
    Core.Cursor.execute("Select COUNT(JournalName) from StudentMagazineRecord WHERE UserName = %s; ", (UserName,))
    return Core.Cursor.fetchone()[0]


def GetUserNameByMagazine(Core: Init, Name: str):
    Core.Cursor.execute("Select UserName from StudentMagazineRecord WHERE JournalName = %s; ", (Name,))
    return Core.Cursor.fetchall()


def GetUserCountByMagazine(Core: Init, Name: str):
    Core.Cursor.execute("Select COUNT(UserName) from StudentMagazineRecord WHERE JournalName = %s; ", (Name,))
    return Core.Cursor.fetchone()[0]


def IsMagazineSubscribedByUser(Core: Init, UserName: str, Magazine: str):
    Core.Cursor.execute("Select * from StudentMagazineRecord WHERE UserName = %s and JournalName = %s; ",
                        (UserName, Magazine))
    if len(Core.Cursor.fetchall()) > 0:
        return True
    return False


def RequestSubscription(Core: Init, UserName: str, Magazine: str, Email: str, Status: int):
    try:
        Core.Cursor.execute("INSERT INTO StudentMagazineRequestRecord(JournalName,UserName,Status , Email) VALUES ("
                            "%s,%s,%s,%s);", (Magazine, UserName, Status, Email))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def GetSubscriptionRequest(Core: Init, SortBY: str = "UserName", Sort: str = "ASC"):
    Core.Cursor.execute("Select JournalName,UserName,Status,Email from StudentMagazineRequestRecord ORDER BY %s %s; ",
                        (SortBY, Sort))
    return Core.Cursor.fetchall()


def GetSubscriptionRequestByStatus(Core: Init, Status: int):
    Core.Cursor.execute(
        "Select JournalName,UserName,Status,Email from StudentMagazineRequestRecord WHERE Status = %s; ",
        (Status,))
    return Core.Cursor.fetchall()


def GetSubscriptionRequestByUsername(Core: Init, Username: str):
    Core.Cursor.execute(
        "Select JournalName,UserName,Status,Email from StudentMagazineRequestRecord WHERE UserName = %s; ",
        (Username,))
    return Core.Cursor.fetchall()


def GetSubscriptionRequestByUsernameAndStatus(Core: Init, Username: str, Status: str):
    Core.Cursor.execute(
        "Select JournalName,UserName,Status,Email from StudentMagazineRequestRecord WHERE UserName = %s AND Status = "
        "%s; ", (Username, Status))
    return Core.Cursor.fetchall()


def GetSubscriptionRequestByJournalName(Core: Init, JournalName: str):
    Core.Cursor.execute(
        "Select JournalName,UserName,Status,Email from StudentMagazineRequestRecord WHERE JournalName = %s; ",
        (JournalName,))
    return Core.Cursor.fetchall()


def GetSubscriptionRequestBy(Core: Init, By: str, Value: str):
    Core.Cursor.execute("Select JournalName,UserName,Status,Email from StudentMagazineRequestRecord WHERE %s = %s; ",
                        (By, Value))
    return Core.Cursor.fetchall()


def SearchMagazineByName(Core: Init, Name: str, N: int, Sort="ASC"):
    Core.Cursor.execute("Select JournalName ,Volume ,Issue ,ReleaseDate , Location from MagazineRecord WHERE "
                        "JournalName like %s ORDER BY JournalName %s; ", (Name, Sort))
    return Core.Cursor.fetchmany(N)


def SearchMagazineByAuthor(Core: Init, Author: str, N: int, Sort="ASC"):
    Core.Cursor.execute("Select JournalName ,Volume ,Issue ,ReleaseDate , Location from MagazineRecord INNER JOIN "
                        "MagazinesAuthorRecord on MagazinesAuthorRecord.JournalName = MagazineRecord.JournalName WHERE"
                        " MagazinesAuthorRecord.Author LIKE %s ORDER BY JournalName %s; ", (Author, Sort))
    return Core.Cursor.fetchmany(N)


def GetMagazinesByName(Core: Init, Name: str):
    Core.Cursor.execute("Select JournalName ,Volume ,Issue ,ReleaseDate , Location from MagazineRecord WHERE "
                        "JournalName = %s; ", (Name,))
    return Core.Cursor.fetchall()


def GetSubscriptionByUserName(Core: Init, Name: str):
    Core.Cursor.execute(
        "Select JournalName,UserName,Email from StudentMagazineRecord WHERE UserName = %s ; ", (Name,))
    return Core.Cursor.fetchall()


def GetSubscriptionByMagazineName(Core: Init, MagazineName: str):
    Core.Cursor.execute(
        "Select JournalName,UserName,Email from StudentMagazineRecord WHERE JournalName = %s ; ", (MagazineName,))
    return Core.Cursor.fetchall()


def UpdateSubscriptionRequestStatus(Core: Init, Status: RequestStatus, ReqNo: int):
    try:
        Core.Cursor.execute("UPDATE StudentMagazineRequestRecord SET Status = %s where ReqNO = %s", (Status, ReqNo))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def AddMagazine(Core: Init, Magazine: str):
    try:
        Core.Cursor.execute("INSERT INTO Magazines(JournalName) VALUES (%s);", (Magazine,))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def AddMagazineRecord(Core: Init, Magazine: str, Volume: str, Issue: str, Date: str, Location: str, Authors: list):
    try:
        Core.Cursor.execute("INSERT INTO MagazineRecord (JournalName ,Volume ,Issue ,ReleaseDate , Location ) VALUES "
                            "(%s,%s,%s,%s,%s);", (Magazine, Volume, Issue, Date, Location))
        Core.Database.commit()
        for i in Authors:
            Core.Cursor.execute(
                "INSERT INTO MagazineAuthorRecord (JournalName ,ReleaseDate , Author ) VALUES "
                "(%s,%s,%s);", (Magazine, Date, i))
            Core.Database.commit()
    except mysql.connector.Error:
        return False


def AddMagazineToUser(Core: Init, UserName: str, Magazine: str, Email: str):
    try:
        Core.Cursor.execute("INSERT INTO StudentMagazineRecord(JournalName,UserName,Email ) VALUES (%s,%s,%s);",
                            (Magazine, UserName, Email))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def RemoveMagazineFromUser(Core: Init, UserName: str, Magazine: str):
    try:
        Core.Cursor.execute("DELETE FROM StudentMagazineRecord WHERE JournalName = %s AND UserName = %s;",
                            (Magazine, UserName))
        Core.Database.commit()
        return True
    except mysql.connector.Error:
        return False


def RemoveMagazineRecord(Core: Init, Magazine: str, Date: str):
    try:
        Core.Cursor.execute("DELETE FROM MagazineRecord WHERE JournalName = %s AND ReleaseDate = %s;", (Magazine, Date))
        Core.Database.commit()
        Core.Cursor.execute("DELETE FROM MagazineAuthorRecord WHERE JournalName = %s AND ReleaseDate = %s;",
                            (Magazine, Date))
        Core.Database.commit()
    except mysql.connector.Error:
        return False


def UpdateMagazineRecord(Core: Init, Magazine: str, Volume: str, Issue: str, Date: str, Location: str, Authors: list):
    if AddMagazineRecord(Core, Magazine, Volume, Issue, Date, Location, Authors):
        return True
    else:
        if RemoveMagazineRecord(Core, Magazine, Date) and AddMagazineRecord(Core, Magazine, Volume, Issue, Date,
                                                                            Location, Authors):
            return True
        return False
