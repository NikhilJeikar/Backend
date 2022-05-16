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


def BookRequestData(RequestID, BookName, Author, RequestBy, Status, Reason):
    Data = {
        "RequestID": RequestID,
        "BookName": BookName,
        "Author": Author,
        "RequestBy": RequestBy,
        "Status": Status,
        "Reason": Reason
    }
    return json.dumps(Data)


def BooksRequestData(Requests):
    List = []
    for Request in Requests:
        List.append(BookRequestData(Request[0], Request[1], Request[2], Request[3], Request[4], Request[5]))
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
        "ReleaseDate": ReleaseDate.strftime("%m/%d/%Y"),
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
        "Status": Email
    }
    return Data


def SubscriptionsData(Subscriptions):
    List = []
    for Subscription in Subscriptions:
        List.append(SubscriptionData(Subscription[0], Subscription[1], Subscription[2]))
    return List


def SubscriptionRequestData(ID, JournalName, UserName, Status, Email):
    Data = {
        "Id": ID,
        "JournalName": JournalName,
        "UserName": UserName,
        "Email": Email,
        "Status": Status
    }
    return Data


def SubscriptionRequestsData(Subscriptions):
    List = []
    for Subscription in Subscriptions:
        List.append(SubscriptionRequestData(Subscription[0], Subscription[1], Subscription[2], Subscription[3],
                                            Subscription[4]))
    return List


def IssueData(IssueID, ISBN, BookName, IssuedTo, dateIssued):
    Data = {
        "IssueID": IssueID,
        "ISBN": ISBN,
        "BookName": BookName,
        "IssuedTo": IssuedTo,
        "dateIssued": dateIssued
    }
    return Data


def IssuesData(Issues):
    List = []
    for Issue in Issues:
        List.append(IssueData(Issue[0], Issue[1], Issue[2], Issue[3], Issues[4]))
    return List


def UserIssueData(ISBN, BookName, dateIssued):
    Data = {
        "ISBN": ISBN,
        "BookName": BookName,
        "DateIssued": dateIssued
    }
    return Data


def UserIssuesData(UserIssues):
    List = []
    for Issue in UserIssues:
        List.append(UserIssueData(Issue[0], Issue[1], Issue[2]))
    return List


def BudgetData(BudgetID, Src, Amount, UsedAmt, Type):
    Data = {
        "BudgetID": BudgetID,
        "Src": Src,
        "Amount": Amount,
        "UsedAmt": UsedAmt,
        "Type": Type
    }
    return Data


def BudgetsData(Budgets):
    List = []
    for budget in Budgets:
        List.append(BudgetData(budget[0], budget[1], budget[2], budget[3], budget[4]))
    return List


def ExpenditureData(InvestedOn, Amount):
    Data = {
        "InvestedOn": InvestedOn,
        "Amount": Amount,
    }
    return Data


def ExpendituresData(Expenditures):
    List = []
    for Expenditure in Expenditures:
        List.append(ExpenditureData(Expenditure[0], Expenditure[1]))
    return List


def RemainingBudgetData(Type, RemainingAmt):
    Data = {
        "Type": Type,
        "RemainingAmt": RemainingAmt,
    }
    return Data


def RemainingBudgetsData(RemainingBudgets):
    List = []
    for RemainingBudget in RemainingBudgets:
        List.append(RemainingBudgetData(RemainingBudget[0], RemainingBudget[1]))
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
        "Issue": "",
        "Reason": "",
        "BudgetAmt": "",
        "UsedBudgetAmt": "",
        "BudgetType": "",
        "InvestedOn": "",
        "BudgetID": "",
        "ExpAmt": ""

    }
