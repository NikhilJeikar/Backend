from Init import Init
from DataGenerator import *
from Queries import *
from Storage import StoreThumbnail, StoreDigitalBooks
from Constants import *
import os


def Parser(Strings):
    return f"{len(Strings)}{Header.Split}{Strings}".encode()


def PDF2Thumbnail(Path: str):
    # Should return path of the image
    return ""


async def WebHandler(CoreObject: Init, Client, Data):
    ID = Data["ID"]
    Request = Data["Header"]
    if Request == Header.Login:
        UserName = Data["UserName"]
        Password = Data["Password"]
        Ret = AuthUser(CoreObject, UserName, Password)
        if Ret is not None:
            await Client.send(Parser(BaseData(Header.Success, Ret)))
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
                    data = SearchISBN(CoreObject, ISBN, Count, Sort)
                    data = BooksData(data)
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
                        Lis += SearchAuthor(CoreObject, Author, int(Count / len(Filters)), Sort)
                    data = BooksData(Lis)
                    await Client.send(Parser(BaseData(Header.Success, data)))
            if GetPrivilegeByID(CoreObject, ID) & Privileges.Admin:
                if Request == Header.Create.User:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User
                    if AddUser(CoreObject, UserName, Password, Permission):
                        await Client.send(Parser(BaseData(Header.Success)))
                    else:
                        await Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Update.BookRecord:
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"].encode()
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        Save.write(File)
                        Save.close()
                        Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                            ThumbnailUrl) and UpdateDigital(CoreObject, ISBN, FileUrl):
                            await Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + Thumbnail)
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
                    Author = Data["Author"]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"].encode()
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        Save.write(File)
                        Save.close()
                        Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                         ThumbnailUrl) and AddDigital(CoreObject, ISBN, FileUrl):
                            await Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + Thumbnail)
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
                        if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                             ThumbnailUrl):
                            await Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                        else:
                            await Client.send(Parser(BaseData(Header.Success)))
                        try:
                            os.remove("FilesCache/" + ISBN + ".jpeg")
                        except FileNotFoundError:
                            pass
            if GetPrivilegeByID(CoreObject, ID) & Privileges.SuperAdmin:
                if Request == Header.Create.Admin:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User + Privileges.Admin
                    if AddUser(CoreObject, UserName, Password, Permission):
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
            Client.send(Parser(BaseData(Header.Success, Ret)))
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
                    data = SearchISBN(CoreObject, ISBN, Count, Sort)
                    data = BooksData(data)
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
                        Lis += SearchAuthor(CoreObject, Author, int(Count / len(Filters)), Sort)
                    data = BooksData(Lis)
                    Client.send(Parser(BaseData(Header.Success, data)))
            if GetPrivilegeByID(CoreObject, ID) & Privileges.Admin:
                if Request == Header.Create.User:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User
                    if AddUser(CoreObject, UserName, Password, Permission):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
                elif Request == Header.Update.BookRecord:
                    Name = Data["BookName"]
                    ISBN = Data["ISBN"]
                    Author = Data["Author"]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"].encode()
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        Save.write(File)
                        Save.close()
                        Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                            ThumbnailUrl) and UpdateDigital(CoreObject, ISBN, FileUrl):
                            Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + Thumbnail)
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
                    Author = Data["Author"]
                    Availability = Data["Availability"]
                    Type = int(Data["Type"])
                    if Type & Avail.Online:
                        File = Data["Book"].encode()
                        Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                        Save.write(File)
                        Save.close()
                        Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                        ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                        FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                        if AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                         ThumbnailUrl) and AddDigital(CoreObject, ISBN, FileUrl):
                            Client.send(Parser(BaseData(Header.Success)))
                        else:
                            RemoveDigital(CoreObject, ISBN)
                            RemoveBookRecord(CoreObject, ISBN)
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))

                        try:
                            os.remove("FilesCache/" + Thumbnail)
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
                        if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                             ThumbnailUrl):
                            Client.send(Parser(BaseData(Header.Failed, Failure.Server)))
                        else:
                            Client.send(Parser(BaseData(Header.Success)))
                        try:
                            os.remove("FilesCache/" + ISBN + ".jpeg")
                        except FileNotFoundError:
                            pass
            if GetPrivilegeByID(CoreObject, ID) & Privileges.SuperAdmin:
                if Request == Header.Create.Admin:
                    UserName = Data["UserName"]
                    Password = Data["Password"]
                    Permission = Privileges.User + Privileges.Admin
                    if AddUser(CoreObject, UserName, Password, Permission):
                        Client.send(Parser(BaseData(Header.Success)))
                    else:
                        Client.send(Parser(BaseData(Header.Failed, Failure=Failure.Exist)))
        else:
            Client.send(Parser(BaseData(Header.Error, Error=Error.Breach)))


async def Handler1WebHandler(Core: Init, Client, Data):
    pass


def Handler1TCPHandler(Core: Init, Client, Data):
    pass
