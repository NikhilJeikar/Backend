from DataGenerator import *
from Queries import *
from ThirdPartyAPI import StoreThumbnail, StoreDigitalBooks, StoreDigitalMagazine
from Constants import *
import os


def Parser(Strings):
    return f"{len(Strings)}{Header.Split}{Strings}".encode()


def PDF2Thumbnail(Path: str):
    # Should return path of the image
    return ""


def List2Bin(File, Data: str):
    Bytes = Data.replace('[', '')
    Bytes = Bytes.replace(']', '')
    Bytes = Bytes.replace(' ', '')
    for i in Bytes.split(','):
        File.write(int(i).to_bytes(1, 'big'))
    File.close()


async def WebHandler(CoreObject: Init, Client, Data):
    ID = Data["ID"]
    Request = Data["Header"]
    if Request == Header.Login:
        UserName = Data["UserName"]
        Password = Data["Password"]
        Ret = AuthUser(CoreObject, UserName, Password)
        if Ret is not None:
            await Client.send(Parser(BaseData(Header.Success, Ret, Misc=GetPrivilegeByID(CoreObject, Ret))))
        else:
            await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Credentials)))
    else:
        if IsUserID(CoreObject, ID):
            if GetPrivilegeByID(CoreObject, ID) & Privileges.User:
                if Request == Header.Update.Password:
                    UserName = GetUsername(CoreObject, ID)
                    CurrPassword = Data["Password"]
                    NewPassword = Data["Misc"]
                    Permission = GetPrivilegeByID(CoreObject, ID)
                    if AuthUser(CoreObject, UserName, CurrPassword):
                        if UpdateUser(CoreObject, UserName, NewPassword, Permission):
                            await Client.send(Parser(BaseData(Header.Success)))
                        else:
                            await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Credentials)))
                elif Request == Header.Fetch.DigitalBooks:
                    Out = GetDigital(CoreObject, Data["ISBN"])
                    if Out == -1:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                    elif Out == -2:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out)))
                elif Request == Header.Fetch.News:
                    Category = Data["Category"]
                    if Category == Header.Categories.Health:
                        await Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Health),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Health)))))
                    elif Category == Header.Categories.Sports:
                        await Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Sports),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Sports)))))
                    elif Category == Header.Categories.General:
                        await Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.General),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.General)))))
                    elif Category == Header.Categories.Science:
                        await Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Science),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Science)))))
                    elif Category == Header.Categories.Business:
                        await Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Business),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Business)))))
                    elif Category == Header.Categories.Entertainment:
                        await Client.send(
                            Parser(BaseData(Header.Success,
                                            NewsData(GetLatestNewsCategory(Header.Categories.Entertainment),
                                                     GetLatestNewsCategoryUpdateTime(
                                                         Header.Categories.Entertainment)))))
                    elif Category == Header.Categories.Technology:
                        await Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Technology
                                                                                           ),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Technology)))))
                    else:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unknown)))
                elif Request == Header.Fetch.BookRecord:
                    ISBN = Data["ISBN"]
                    Count = Data["Count"]
                    Sort = Data["Sort"]
                    data = BooksData(SearchISBN(CoreObject, ISBN, Count, Sort))
                    await Client.send(Parser(BaseData(Header.Success, data)))
                elif Request == Header.Search.Books:
                    Count = Data["Count"]
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"]
                    Sort = Data["Sort"]
                    Filters = Data["SearchFilter"]
                    Lis = []
                    if BookParams.Name in Filters:
                        Lis += SearchBookName(CoreObject, Name, int(Count / len(Filters)), Sort)
                    if BookParams.ISBN in Filters:
                        Lis += SearchISBN(CoreObject, ISBN, int(Count / len(Filters)), Sort)
                    if BookParams.Author in Filters:
                        Lis += SearchAuthor(CoreObject, Author[0], int(Count / len(Filters)), Sort)

                    await Client.send(Parser(BaseData(Header.Success, BooksData(Lis))))
                elif Request == Header.Add.BookRequest:
                    BookName = Data["BookName"]
                    Author = Data["Author"][0]
                    User = Data["UserName"]
                    if RequestBooks(CoreObject, BookName, Author, User):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                elif Request == Header.Fetch.BookRequestStatus:
                    Status = Data["Status"]
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if UserName == GetUsername(CoreObject, ID):
                        if Status != "":
                            Out = GetBookRequestsByUserNameAndStatus(CoreObject, UserName, Status)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                        else:
                            Out = GetBookRequestsByUserName(CoreObject, UserName)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))
                elif Request == Header.Add.MagazineSubscriptionRequest:
                    UserName = Data["UserName"]
                    MagazineName = Data["BookName"]
                    Email = Data["Email"]
                    if IsMagazineSubscribedByUser(CoreObject, UserName, MagazineName):
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                    else:
                        if RequestSubscription(CoreObject, UserName, MagazineName, Email, RequestStatus.processing):
                            await Client.send(Parser(BaseData(Header.Success)))
                        else:
                            await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                elif Request == Header.Search.Magazines:
                    MagazineName = Data["BookName"]
                    Filters = Data["SearchFilter"]
                    Author = Data["Author"]
                    Count = Data["Count"]
                    Sort = Data["Sort"]
                    Lis = []
                    if MagazineParams.Name in Filters:
                        Lis += SearchMagazineByName(CoreObject, MagazineName, int(Count / len(Filters)), Sort)
                    if MagazineParams.Author in Filters:
                        Lis += SearchMagazineByAuthor(CoreObject, Author, int(Count / len(Filters)), Sort)
                    await Client.send(Parser(BaseData(Header.Success, Data=MagazinesData(Lis))))
                elif Request == Header.Fetch.Magazine:
                    Magazine = Data["BookName"]
                    Issue = Data["Issue"]
                    Volume = Data["Volume"]
                    await Client.send(
                        Parser(BaseData(Header.Success, Data=GetMagazinePath(CoreObject, Magazine, Volume, Issue))))
                elif Request == Header.Fetch.MyMagazineRequest:
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    Status = Data["Status"]
                    if UserName == GetUsername(CoreObject, ID):
                        if Status != "":
                            Out = GetSubscriptionRequestByUsernameAndStatus(CoreObject, UserName, Status)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = SubscriptionRequestsData(Out)
                            else:
                                Out = SubscriptionRequestsData(Out[LLimit:ULimit])
                        else:
                            Out = GetSubscriptionRequestByUsername(CoreObject, UserName)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = SubscriptionRequestsData(Out)
                            else:
                                Out = SubscriptionRequestsData(Out[LLimit:ULimit])
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))
                elif Request == Header.Fetch.MySubscription:
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if UserName == GetUsername(CoreObject, ID):
                        Out = GetSubscriptionByUserName(CoreObject, UserName)
                        Count = len(Out)
                        if ULimit < 0:
                            Out = SubscriptionsData(Out)
                        else:
                            Out = SubscriptionsData(Out[LLimit:ULimit])
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))
                elif Request == Header.Add.BookRenewal:
                    UserName = GetUsername(CoreObject, ID)
                    Result = BookRenewal(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.BookReturn:
                    UserName = GetUsername(CoreObject, ID)
                    Result = BookReturn(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.BookReserve:
                    UserName = GetUsername(CoreObject, ID)
                    Result = BookReserval(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.FinePayment:
                    UserName = GetUsername(CoreObject, ID)
                    Result = FinePayment(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Fetch.UserIssuedBook:
                    Username = Data['Username']
                    Result = BooksIssuedUser(CoreObject, Username)
                    Count = len(Result)
                    Out = UserIssuesData(Result)
                    if Out:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.BookSuggestion:
                    Username = Data['Username']
                    Result = booksSuggestion(CoreObject, Username)
                    Count = len(Result)
                    Out = BooksData(Result)
                    if Out:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.UserIssuedBook:
                    Username = Data['Username']
                    Result = BooksIssuedUser(CoreObject, Username)
                    Count = len(Result)
                    Out = BooksData(Result)
                    if Out:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))

            if GetPrivilegeByID(CoreObject, ID) & Privileges.Admin:
                if Request == Header.Update.BookRecord:
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"][0]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"].encode()
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        Save.write(File)
                        Save.close()
                        File = Data["Thumbnail"].encode()
                        Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                        Save.write(File)
                        Save.close()
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg",
                                                      "FilesCache/" + ISBN + ".jpeg")
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                            ThumbnailUrl) and UpdateDigital(CoreObject, ISBN, FileUrl):
                            await Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + ISBN + ".jpeg")
                            os.remove("FilesCache/" + ISBN + ".pdf")
                        except FileNotFoundError:
                            pass
                    else:
                        File = Data["Thumbnail"].encode()
                        Save = open("FilesCache/" + ISBN + ".jpg", 'wb')
                        Save.write(File)
                        Save.close()
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg",
                                                      "FilesCache/" + ISBN + ".jpeg")
                        if not UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                                ThumbnailUrl):
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                        else:
                            await Client.send(Parser(BaseData(Header.Success)))
                        try:
                            os.remove("FilesCache/" + ISBN + ".jpeg")
                        except FileNotFoundError:
                            pass
                elif Request == Header.Add.BookRecord:
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"][0]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"]
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        List2Bin(Save, File)

                        File = Data["Thumbnail"]
                        Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                        List2Bin(Save, File)

                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpg",
                                                      "FilesCache/" + ISBN + ".jpg")
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                         ThumbnailUrl) and AddDigital(CoreObject, ISBN, FileUrl):
                            await Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + ISBN + ".jpg")
                            os.remove("FilesCache/" + ISBN + ".pdf")
                        except FileNotFoundError:
                            pass
                    else:
                        File = Data["Thumbnail"]
                        Save = open("FilesCache/" + ISBN + ".jpg", 'wb')
                        List2Bin(Save, File)
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpg",
                                                      "FilesCache/" + ISBN + ".jpg")
                        if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                             ThumbnailUrl):
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                        else:
                            await Client.send(Parser(BaseData(Header.Success)))
                        try:
                            os.remove("FilesCache/" + ISBN + ".jpg")
                        except FileNotFoundError:
                            pass
                elif Request == Header.Fetch.BookRequest:
                    Status = Data["Status"]
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if UserName != "":
                        if Status != "":
                            Out = GetBookRequestsByUserNameAndStatus(CoreObject, UserName, Status)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                        else:
                            Out = GetBookRequestsByUserName(CoreObject, UserName)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        if Status != "":
                            Out = GetBookRequestsByStatus(CoreObject, Status)
                            Count = len(Data)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                        else:
                            Out = GetBookRequests(CoreObject)
                            Count = len(Data)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Update.BookRequest:
                    RequestID = Data["Misc"]
                    Status = Data["Status"]
                    Admin = GetUsername(CoreObject, ID)
                    Reason = Data["Reason"]
                    if UpdateBookRequestStatus(CoreObject, Status, RequestID, Admin, Reason):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                elif Request == Header.Fetch.MagazineRequest:
                    Status = Data["Status"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if Status == "":
                        Out = GetSubscriptionRequest(CoreObject)
                        Count = len(Out)
                        if ULimit < 0:
                            Out = SubscriptionRequestsData(Out)
                        else:
                            Out = BooksRequestData(Out[LLimit:ULimit])
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        Out = GetSubscriptionRequestByStatus(CoreObject, Status)
                        Count = len(Out)
                        if ULimit < 0:
                            Out = SubscriptionRequestsData(Out)
                        else:
                            Out = BooksRequestData(Out[LLimit:ULimit])
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Update.MagazineRequest:
                    RequestID = Data["Misc"]
                    Status = Data["Status"]
                    if UpdateSubscriptionRequestStatus(CoreObject, Status, RequestID):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                elif Request == Header.Add.MagazineRecord:
                    Authors = Data["Author"]
                    MagazineName = Data["BookName"]
                    Volume = Data["Volume"]
                    Issue = Data["Issue"]
                    ReleaseDate = Data["Misc"]
                    File = Data["Book"].encode()
                    Save = open("FilesCache/" + MagazineName + "-" + ReleaseDate.replace("/", "-") + ".pdf", 'wb')
                    Save.write(File)
                    Save.close()
                    FileUrl = StoreDigitalMagazine(CoreObject.Storage, MagazineName + "-" + ReleaseDate + ".pdf",
                                                   "FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    AddMagazine(CoreObject, MagazineName)
                    if AddMagazineRecord(CoreObject, MagazineName, Volume,
                                         Issue, ReleaseDate, FileUrl,
                                         Authors):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        RemoveMagazineRecord(CoreObject, MagazineName, ReleaseDate)

                        await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                    try:
                        os.remove("FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    except FileNotFoundError:
                        pass
                elif Request == Header.Update.MagazineRecord:
                    Authors = Data["Author"]
                    MagazineName = Data["BookName"]
                    Volume = Data["Volume"]
                    Issue = Data["Issue"]
                    ReleaseDate = Data["Misc"]
                    File = Data["Book"].encode()
                    Save = open("FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf", 'wb')
                    Save.write(File)
                    Save.close()
                    FileUrl = StoreDigitalMagazine(CoreObject.Storage, MagazineName + "-" + ReleaseDate + ".pdf",
                                                   "FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    if UpdateMagazineRecord(CoreObject, MagazineName, Volume, Issue, ReleaseDate, FileUrl, Authors):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        RemoveMagazineRecord(CoreObject, MagazineName, ReleaseDate)

                        await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                    try:
                        os.remove("FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    except FileNotFoundError:
                        pass

                elif Request == Header.Fetch.DueUsers:
                    Result = ViewUsersWithDues(CoreObject)
                    Count = len(Result)
                    Result = IssuesData(Result)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result, Misc=Count)))
                elif Request == Header.Add.BookIssue:
                    Result = IssueBook(CoreObject, Data["ISBN"], Data["UserName"])
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Fetch.TotalBudget:
                    Result = viewTotalBudget(CoreObject)
                    Count = len(Result)
                    Out = BudgetsData(Result)
                    if Out:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.RemainingBudget:
                    Result = viewRemainingBudget(CoreObject)
                    Count = len(Result)
                    Out = RemainingBudgetsData(Result)
                    if Out:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.BudgetDistribution:
                    Result = budgetDistribution(CoreObject)
                    Count = len(Result)
                    Out = ExpendituresData(Result)
                    if Out:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Add.BudgetRecord:
                    Src = Data['Src']
                    Amt = Data['BudgetAmt']
                    UsedAmt = Data['UsedBudgetAmt']
                    Type = Data['BudgetType']
                    Result = InsertBudgetDetails(CoreObject, Src, Amt, UsedAmt, Type)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.ExpenditureRecord:
                    Bid = Data['BudgetID']
                    Invest = Data['InvestedOn']
                    Amt = Data['ExpAmt']
                    Result = InsertExpDetails(CoreObject, Bid, Invest, Amt)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Remove.DeleteHistory:
                    ISBN = Data['ISBN']
                    Result = PermanentDelete(CoreObject, ISBN)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Fetch.DeleteHistory:
                    Result = ReadDeleteHistory(CoreObject)
                    Count = len(Result)
                    Result = BooksData(Result)
                    if Result:
                        await Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        await Client.send(Parser(BaseData(Header.Success, Data=Result,Misc=Count)))

            if GetPrivilegeByID(CoreObject, ID) & Privileges.SuperAdmin:
                if Request == Header.Create.User:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User
                    if AddUser(CoreObject, UserName, Password, Permission):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Create.Admin:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User + Privileges.Admin
                    if AddUser(CoreObject, UserName, Password, Permission):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Remove.UserRecord:
                    UserName = Data["UserName"]
                    if RemoveUser(CoreObject, UserName):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Update.UserStatus:
                    UserName = Data["UserName"]
                    Status = Data["Status"]
                    if UpdateUserStatus(CoreObject, UserName, int(Status)):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))

        else:
            await Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))


def TCPHandler(CoreObject: Init, Client, Data):
    ID = Data["ID"]
    Request = Data["Header"]
    if Request == Header.Login:
        UserName = Data["UserName"]
        Password = Data["Password"]
        Ret = AuthUser(CoreObject, UserName, Password)
        if Ret is not None:
            Client.send(Parser(BaseData(Header.Success, Ret, Misc=GetPrivilegeByID(CoreObject, Ret))))
        else:
            Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Credentials)))
    else:
        if IsUserID(CoreObject, ID):
            if GetPrivilegeByID(CoreObject, ID) & Privileges.User:
                if Request == Header.Update.Password:
                    UserName = GetUsername(CoreObject, ID)
                    CurrPassword = Data["Password"]
                    NewPassword = Data["Misc"]
                    Permission = GetPrivilegeByID(CoreObject, ID)
                    if AuthUser(CoreObject, UserName, CurrPassword):
                        if UpdateUser(CoreObject, UserName, NewPassword, Permission):
                            Client.send(Parser(BaseData(Header.Success)))
                        else:
                            Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Credentials)))
                elif Request == Header.Fetch.DigitalBooks:
                    Out = GetDigital(CoreObject, Data["ISBN"])
                    if Out == -1:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                    elif Out == -2:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Out)))
                elif Request == Header.Fetch.News:
                    Category = Data["Category"]
                    if Category == Header.Categories.Health:
                        Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Health),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Health)))))
                    elif Category == Header.Categories.Sports:
                        Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Sports),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Sports)))))
                    elif Category == Header.Categories.General:
                        Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.General),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.General)))))
                    elif Category == Header.Categories.Science:
                        Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Science),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Science)))))
                    elif Category == Header.Categories.Business:
                        Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Business),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Business)))))
                    elif Category == Header.Categories.Entertainment:
                        Client.send(
                            Parser(BaseData(Header.Success,
                                            NewsData(GetLatestNewsCategory(Header.Categories.Entertainment),
                                                     GetLatestNewsCategoryUpdateTime(
                                                         Header.Categories.Entertainment)))))
                    elif Category == Header.Categories.Technology:
                        Client.send(
                            Parser(BaseData(Header.Success, NewsData(GetLatestNewsCategory(Header.Categories.Technology
                                                                                           ),
                                                                     GetLatestNewsCategoryUpdateTime(
                                                                         Header.Categories.Technology)))))
                    else:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unknown)))
                elif Request == Header.Fetch.BookRecord:
                    ISBN = Data["ISBN"]
                    Count = Data["Count"]
                    Sort = Data["Sort"]
                    data = BooksData(SearchISBN(CoreObject, ISBN, Count, Sort))
                    Client.send(Parser(BaseData(Header.Success, data)))
                elif Request == Header.Search.Books:
                    Count = Data["Count"]
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"]
                    Sort = Data["Sort"]
                    Filters = Data["SearchFilter"]
                    Lis = []
                    if BookParams.Name in Filters:
                        Lis += SearchBookName(CoreObject, Name, int(Count / len(Filters)), Sort)
                    if BookParams.ISBN in Filters:
                        Lis += SearchISBN(CoreObject, ISBN, int(Count / len(Filters)), Sort)
                    if BookParams.Author in Filters:
                        Lis += SearchAuthor(CoreObject, Author[0], int(Count / len(Filters)), Sort)

                    Client.send(Parser(BaseData(Header.Success, BooksData(Lis))))
                elif Request == Header.Add.BookRequest:
                    BookName = Data["BookName"]
                    Author = Data["Author"][0]
                    User = Data["UserName"]
                    if RequestBooks(CoreObject, BookName, Author, User):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                elif Request == Header.Fetch.BookRequestStatus:
                    Status = Data["Status"]
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if UserName == GetUsername(CoreObject, ID):
                        if Status != "":
                            Out = GetBookRequestsByUserNameAndStatus(CoreObject, UserName, Status)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                        else:
                            Out = GetBookRequestsByUserName(CoreObject, UserName)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))
                elif Request == Header.Add.MagazineSubscriptionRequest:
                    UserName = Data["UserName"]
                    MagazineName = Data["BookName"]
                    Email = Data["Email"]
                    if IsMagazineSubscribedByUser(CoreObject, UserName, MagazineName):
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                    else:
                        if RequestSubscription(CoreObject, UserName, MagazineName, Email, RequestStatus.processing):
                            Client.send(Parser(BaseData(Header.Success)))
                        else:
                            Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Server)))
                elif Request == Header.Search.Magazines:
                    MagazineName = Data["BookName"]
                    Filters = Data["SearchFilter"]
                    Author = Data["Author"]
                    Count = Data["Count"]
                    Sort = Data["Sort"]
                    Lis = []
                    if MagazineParams.Name in Filters:
                        Lis += SearchMagazineByName(CoreObject, MagazineName, int(Count / len(Filters)), Sort)
                    if MagazineParams.Author in Filters:
                        Lis += SearchMagazineByAuthor(CoreObject, Author, int(Count / len(Filters)), Sort)
                    Client.send(Parser(BaseData(Header.Success, Data=MagazinesData(Lis))))
                elif Request == Header.Fetch.Magazine:
                    Magazine = Data["BookName"]
                    Issue = Data["Issue"]
                    Volume = Data["Volume"]
                    Client.send(
                        Parser(BaseData(Header.Success, Data=GetMagazinePath(CoreObject, Magazine, Volume, Issue))))
                elif Request == Header.Fetch.MyMagazineRequest:
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    Status = Data["Status"]
                    if UserName == GetUsername(CoreObject, ID):
                        if Status != "":
                            Out = GetSubscriptionRequestByUsernameAndStatus(CoreObject, UserName, Status)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = SubscriptionRequestsData(Out)
                            else:
                                Out = SubscriptionRequestsData(Out[LLimit:ULimit])
                        else:
                            Out = GetSubscriptionRequestByUsername(CoreObject, UserName)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = SubscriptionRequestsData(Out)
                            else:
                                Out = SubscriptionRequestsData(Out[LLimit:ULimit])
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))
                elif Request == Header.Fetch.MySubscription:
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if UserName == GetUsername(CoreObject, ID):
                        Out = GetSubscriptionByUserName(CoreObject, UserName)
                        Count = len(Out)
                        if ULimit < 0:
                            Out = SubscriptionsData(Out)
                        else:
                            Out = SubscriptionsData(Out[LLimit:ULimit])
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))
                elif Request == Header.Add.BookRenewal:
                    UserName = GetUsername(CoreObject, ID)
                    Result = BookRenewal(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.BookReturn:
                    UserName = GetUsername(CoreObject, ID)
                    Result = BookReturn(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.BookReserve:
                    UserName = GetUsername(CoreObject, ID)
                    Result = BookReserval(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.FinePayment:
                    UserName = GetUsername(CoreObject, ID)
                    Result = FinePayment(CoreObject, Data["ISBN"], UserName)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Fetch.UserIssuedBook:
                    Username = Data['Username']
                    Result = BooksIssuedUser(CoreObject, Username)
                    Count = len(Result)
                    Out = UserIssuesData(Result)
                    if Out:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.BookSuggestion:
                    Username = Data['Username']
                    Result = booksSuggestion(CoreObject, Username)
                    Count = len(Result)
                    Out = BooksData(Result)
                    if Out:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))

            if GetPrivilegeByID(CoreObject, ID) & Privileges.Admin:
                if Request == Header.Update.BookRecord:
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"][0]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"].encode()
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        Save.write(File)
                        Save.close()
                        File = Data["Thumbnail"].encode()
                        Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                        Save.write(File)
                        Save.close()
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg",
                                                      "FilesCache/" + ISBN + ".jpeg")
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                            ThumbnailUrl) and UpdateDigital(CoreObject, ISBN, FileUrl):
                            Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + ISBN + ".jpeg")
                            os.remove("FilesCache/" + ISBN + ".pdf")
                        except FileNotFoundError:
                            pass
                    else:
                        File = Data["Thumbnail"].encode()
                        Save = open("FilesCache/" + ISBN + ".jpg", 'wb')
                        Save.write(File)
                        Save.close()
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg",
                                                      "FilesCache/" + ISBN + ".jpeg")
                        if not UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                                ThumbnailUrl):
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                        else:
                            Client.send(Parser(BaseData(Header.Success)))
                        try:
                            os.remove("FilesCache/" + ISBN + ".jpeg")
                        except FileNotFoundError:
                            pass
                elif Request == Header.Add.BookRecord:
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"][0]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"]
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        List2Bin(Save, File)

                        File = Data["Thumbnail"]
                        Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                        List2Bin(Save, File)

                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpg",
                                                      "FilesCache/" + ISBN + ".jpg")
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                         ThumbnailUrl) and AddDigital(CoreObject, ISBN, FileUrl):
                            Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + ISBN + ".jpg")
                            os.remove("FilesCache/" + ISBN + ".pdf")
                        except FileNotFoundError:
                            pass
                    else:
                        File = Data["Thumbnail"]
                        Save = open("FilesCache/" + ISBN + ".jpg", 'wb')
                        List2Bin(Save, File)
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpg",
                                                      "FilesCache/" + ISBN + ".jpg")
                        if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                             ThumbnailUrl):
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                        else:
                            Client.send(Parser(BaseData(Header.Success)))
                        try:
                            os.remove("FilesCache/" + ISBN + ".jpg")
                        except FileNotFoundError:
                            pass
                elif Request == Header.Fetch.BookRequest:
                    Status = Data["Status"]
                    UserName = Data["UserName"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if UserName != "":
                        if Status != "":
                            Out = GetBookRequestsByUserNameAndStatus(CoreObject, UserName, Status)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                        else:
                            Out = GetBookRequestsByUserName(CoreObject, UserName)
                            Count = len(Out)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        if Status != "":
                            Out = GetBookRequestsByStatus(CoreObject, Status)
                            Count = len(Data)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                        else:
                            Out = GetBookRequests(CoreObject)
                            Count = len(Data)
                            if ULimit < 0:
                                Out = BooksRequestData(Out)
                            else:
                                Out = BooksRequestData(Out[LLimit:ULimit])
                            Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Update.BookRequest:
                    RequestID = Data["Misc"]
                    Status = Data["Status"]
                    Admin = GetUsername(CoreObject, ID)
                    Reason = Data["Reason"]
                    if UpdateBookRequestStatus(CoreObject, Status, RequestID, Admin, Reason):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                elif Request == Header.Fetch.MagazineRequest:
                    Status = Data["Status"]
                    ULimit = Data["Range"][0]
                    LLimit = Data["Range"][1]
                    if Status == "":
                        Out = GetSubscriptionRequest(CoreObject)
                        Count = len(Out)
                        if ULimit < 0:
                            Out = SubscriptionRequestsData(Out)
                        else:
                            Out = BooksRequestData(Out[LLimit:ULimit])
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                    else:
                        Out = GetSubscriptionRequestByStatus(CoreObject, Status)
                        Count = len(Out)
                        if ULimit < 0:
                            Out = SubscriptionRequestsData(Out)
                        else:
                            Out = BooksRequestData(Out[LLimit:ULimit])
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Update.MagazineRequest:
                    RequestID = Data["Misc"]
                    Status = Data["Status"]
                    if UpdateSubscriptionRequestStatus(CoreObject, Status, RequestID):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                elif Request == Header.Add.MagazineRecord:
                    Authors = Data["Author"]
                    MagazineName = Data["BookName"]
                    Volume = Data["Volume"]
                    Issue = Data["Issue"]
                    ReleaseDate = Data["Misc"]
                    File = Data["Book"].encode()
                    Save = open("FilesCache/" + MagazineName + "-" + ReleaseDate.replace("/", "-") + ".pdf", 'wb')
                    Save.write(File)
                    Save.close()
                    FileUrl = StoreDigitalMagazine(CoreObject.Storage, MagazineName + "-" + ReleaseDate + ".pdf",
                                                   "FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    AddMagazine(CoreObject, MagazineName)
                    if AddMagazineRecord(CoreObject, MagazineName, Volume,
                                         Issue, ReleaseDate, FileUrl,
                                         Authors):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        RemoveMagazineRecord(CoreObject, MagazineName, ReleaseDate)

                        Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                    try:
                        os.remove("FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    except FileNotFoundError:
                        pass
                elif Request == Header.Update.MagazineRecord:
                    Authors = Data["Author"]
                    MagazineName = Data["BookName"]
                    Volume = Data["Volume"]
                    Issue = Data["Issue"]
                    ReleaseDate = Data["Misc"]
                    File = Data["Book"].encode()
                    Save = open("FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf", 'wb')
                    Save.write(File)
                    Save.close()
                    FileUrl = StoreDigitalMagazine(CoreObject.Storage, MagazineName + "-" + ReleaseDate + ".pdf",
                                                   "FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    if UpdateMagazineRecord(CoreObject, MagazineName, Volume, Issue, ReleaseDate, FileUrl, Authors):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        RemoveMagazineRecord(CoreObject, MagazineName, ReleaseDate)

                        Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                    try:
                        os.remove("FilesCache/" + MagazineName + "-" + ReleaseDate + ".pdf")
                    except FileNotFoundError:
                        pass

                elif Request == Header.Fetch.DueUsers:
                    Result = ViewUsersWithDues(CoreObject)
                    Count = len(Result)
                    Result = IssuesData(Result)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result, Misc=Count)))
                elif Request == Header.Add.BookIssue:
                    Result = IssueBook(CoreObject, Data["ISBN"], Data["UserName"])
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Fetch.TotalBudget:
                    Result = viewTotalBudget(CoreObject)
                    Count = len(Result)
                    Out = BudgetsData(Result)
                    if Out:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.RemainingBudget:
                    Result = viewRemainingBudget(CoreObject)
                    Count = len(Result)
                    Out = RemainingBudgetsData(Result)
                    if Out:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Fetch.BudgetDistribution:
                    Result = budgetDistribution(CoreObject)
                    Count = len(Result)
                    Out = ExpendituresData(Result)
                    if Out:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Out, Misc=Count)))
                elif Request == Header.Add.BudgetRecord:
                    Src = Data['Src']
                    Amt = Data['BudgetAmt']
                    UsedAmt = Data['UsedBudgetAmt']
                    Type = Data['BudgetType']
                    Result = InsertBudgetDetails(CoreObject, Src, Amt, UsedAmt, Type)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Add.ExpenditureRecord:
                    Bid = Data['BudgetID']
                    Invest = Data['InvestedOn']
                    Amt = Data['ExpAmt']
                    Result = InsertExpDetails(CoreObject, Bid, Invest, Amt)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Remove.DeleteHistory:
                    ISBN = Data['ISBN']
                    Result = PermanentDelete(CoreObject, ISBN)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result)))
                elif Request == Header.Fetch.DeleteHistory:
                    Result = ReadDeleteHistory(CoreObject)
                    Count = len(Result)
                    Result = BooksData(Result)
                    if Result:
                        Client.send(Parser(BaseData(Header.Error, Error=Error.Unavailable)))
                    else:
                        Client.send(Parser(BaseData(Header.Success, Data=Result,Misc=Count)))
                elif Request == Header.Remove.BookRecord:
                    ISBN = Data['ISBN']
                    if RemoveBookRecord(CoreObject, ISBN):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))

            if GetPrivilegeByID(CoreObject, ID) & Privileges.SuperAdmin:
                if Request == Header.Create.User:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User
                    if AddUser(CoreObject, UserName, Password, Permission):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Create.Admin:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User + Privileges.Admin
                    if AddUser(CoreObject, UserName, Password, Permission):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Remove.UserRecord:
                    UserName = Data["UserName"]
                    if RemoveUser(CoreObject, UserName):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Update.UserStatus:
                    UserName = Data["UserName"]
                    Status = Data["Status"]
                    if UpdateUserStatus(CoreObject, UserName, int(Status)):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))

        else:
            Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))