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
    return json.dumps(Data)


def BooksData(Books):
    List = []
    for book in Books:
        List.append(BookData(book[1], book[0], book[3], book[5], book[5], book[2]))
    return List


def RequestData(RequestID, BookName, Author, RequestBy, Status):
    Data = {
        "RequestID": RequestID,
        "BookName": BookName,
        "Author": Author,
        "RequestBy": RequestBy,
        "Status": Status
    }
    return json.dumps(Data)


def RequestsData(Requests):
    List = []
    for Request in Requests:
        List.append(RequestData(Request[0], Request[1], Request[2], Request[3], Request[4]))
    return List


def NewsData(News, Time):
    Data = {
        "News": News,
        "Time": Time
    }
    return json.dumps(Data)


def Stats(Header, Success, Failure):
    Data = {
        "Header": Header,
        "Success": Success,
        "Failure": Failure
    }
    return json.dumps(Data)


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
        "Author": "",
        "Type": "",
        "Time": "",
        "Availability": "",
        "Thumbnail": "",
        "SearchFilter": [],
        "Category": "",
        "Book": "",
        "Count": "",
        "Misc": "",
        "Sort": "",
        "Range": [],
        "Status": ""
    }
