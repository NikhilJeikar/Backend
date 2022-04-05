import json


def BaseData(Header, Data="", Failure="", Error="", Misc=""):
    Data = {
        "Header": Header,
        "Data": Data,
        "Failure": Failure,
        "Error": Error,
        "Misc": Misc
    }
    return json.dumps(Data)


def BookData(ISBN, BookName, Author, Availability, Type, Thumbnail):
    Data = {
        "ISBN": ISBN,
        "BookName": BookName,
        "Author": Author,
        "Availability": Availability,
        "Type": Type,
        "Thumbnail": Thumbnail
    }
    return Data


def BooksData(Books):
    List = []
    for book in Books:
        List.append(BookData(book[1], book[0], book[3], book[5], book[5], book[2]))
    return List


def BookRequestData(RequestID, BookName, Author, RequestBy, Status):
    Data = {
        "RequestID": RequestID,
        "BookName": BookName,
        "Author": Author,
        "RequestBy": RequestBy,
        "Status": Status
    }
    return json.dumps(Data)


def BooksRequestData(Requests):
    List = []
    for Request in Requests:
        List.append(BookRequestData(Request[0], Request[1], Request[2], Request[3], Request[4]))
    return List


def NewsData(News, Time):
    Data = {
        "News": News,
        "Time": Time
    }
    return Data


def MagazineData(Name, Volume, Issue, ReleaseDate, Location):
    Data = {
        "Name": Name,
        "Volume": Volume,
        "Issue": Issue,
        "ReleaseDate": ReleaseDate,
        "Location": Location
    }
    return Data


def MagazinesData(Magazines):
    List = []
    for Magazine in Magazines:
        List.append(MagazineData(Magazine[0], Magazine[1], Magazine[2], Magazine[3], Magazine[4]))
    return List


def SubscriptionData(JournalName, UserName, Email):
    Data = {
        "JournalName": JournalName,
        "UserName": UserName,
        "Email": Email
    }
    return Data


def SubscriptionsData(Subscriptions):
    List = []
    for Subscription in Subscriptions:
        List.append(SubscriptionData(Subscription[0], Subscription[1], Subscription[2]))
    return List


def SubscriptionRequestData(JournalName, UserName, Email, Status):
    Data = {
        "JournalName": JournalName,
        "UserName": UserName,
        "Email": Email,
        "Status": Status
    }
    return Data


def SubscriptionRequestsData(Subscriptions):
    List = []
    for Subscription in Subscriptions:
        List.append(SubscriptionData(Subscription[0], Subscription[1], Subscription[2]))
    return List


def Request():
    Data = {
        "ID": "",
        "Handler": "",
        "Header": "",
        "UserName": "",
        "Password": "",
        "Permission": "",
        "ISBN": "",
        "BookName": "",
        "Author": [],
        "Type": "",
        "Availability": "",
        "Thumbnail": "",
        "SearchFilter": [],
        "Category": "",
        "Book": "",
        "Count": "",
        "Misc": "",
        "Sort": "",
        "Range": [],
        "Status": "",
        "Email": "",
        "Volume": "",
        "Issue": ""
    }
