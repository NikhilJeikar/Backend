from typing import List
from Init import Init
from Queries import *
from Storage import StoreThumbnail, StoreDigitalBooks
from Constants import *
import pandas as pd
from io import StringIO
import os


def Parser(Strings: list):
    print(Strings)
    Data = Header.Split.join(Strings)
    return f"{len(Data)}{Header.Split}{Data}".encode()


def FetchManyParser(Data: List[tuple]):
    Temp = []
    for i in Data:
        _ = Header.Split.join(i)
        Temp.append(_)
    return [Header.Split.join(Temp)]


def PDF2Thumbnail(Path: str):
    # Should return path of the image
    return ""


async def NikhilWebHandler(CoreObject: Init, Client, ID: str, Command: str, Path: str = None):
    Base, Rem = Command.split(sep=Header.Split, maxsplit=1)
    if Base == Header.Login:
        Username, Password = Rem.split(sep=Header.Split)
        Return = AuthUser(CoreObject, Username, Password)
        print("Return", Return)
        if Return is not None:
            await Client.send(Parser([Header.Success, Return]))
        else:
            await Client.send(Parser([Header.Failed]))
    elif Base == Header.Create.User:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.Admin or GetPrivilegeByID(CoreObject,
                                                                                    ID) == Privileges.SuperAdmin:
            Username, Password = Rem.split(sep=Header.Split)
            if AddUser(CoreObject, Username, Password, Privileges.User):
                await Client.send(Parser([Header.Success]))
            else:
                await Client.send(Parser([Header.Failed, Failure.Exist]))
        else:
            await Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Admin:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.SuperAdmin:
            Username, Password = Rem.split(sep=Header.Split)
            if AddUser(CoreObject, Username, Password, Privileges.Admin):
                await Client.send(Parser([Header.Success]))
            else:
                await Client.send(Parser([Header.Failed, Failure.Exist]))
        else:
            await Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Users:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.Admin or GetPrivilegeByID(CoreObject,
                                                                                    ID) == Privileges.SuperAdmin:
            try:
                Data = pd.read_csv(Rem)
                Data = StringIO(Data)
                Df = pd.read_csv(Data, header=None)
                Success = 0
                Failed = 0
                FailedName = []
                for i in Df.index:
                    if AddUser(CoreObject, Df.loc[i][0], Df.loc[i][1], Privileges.User):
                        Success += 1
                    else:
                        Failed += 1
                        FailedName.append(Df.loc[i][0])
                push = [Header.Success, str(Success), Header.Failed, str(Failed)]
                push.extend(FailedName)
                await Client.send(Parser(push))
            except:
                await Client.send(Parser([Header.Error, Error.Read]))

        else:
            await Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Admins:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.SuperAdmin:
            try:
                Data = pd.read_csv(Rem)
                Data = StringIO(Data)
                Df = pd.read_csv(Data, header=None)
                Success = 0
                Failed = 0
                FailedName = []
                for i in Df.index:
                    if AddUser(CoreObject, Df.loc[i][0], Df.loc[i][1], Privileges.Admin):
                        Success += 1
                    else:
                        Failed += 1
                        FailedName.append(Df.loc[i][0])
                push = [Header.Success, str(Success), Header.Failed, str(Failed)]
                push.extend(FailedName)
                await Client.send(Parser(push))
            except:
                await Client.send(Parser([Header.Error, Error.Read]))

        else:
            await Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Update.Permission:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.SuperAdmin:
            Username, Permission = Rem.split(sep=Header.Split)
            if Permission != Privileges.SuperAdmin:
                if UpdateUser(CoreObject, Username, GetPasswordByUsername(CoreObject, Username), Permission):
                    await Client.send(Parser([Header.Success]))
                else:
                    await Client.send(Parser([Header.Failed, Failure.Server]))
            else:
                await Client.send(Parser([Header.Failed, Failure.Exist]))
        else:
            await Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Update.Password:
        if UpdateUser(CoreObject, GetUsername(CoreObject, ID), Rem, GetPrivilegeByID(CoreObject, ID)):
            await Client.send(Parser([Header.Success]))
        else:
            await Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Update.BookRecord:
        try:
            Name, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            ISBN, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Author, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Availability, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Type, Rem = Rem.splitRem.split(sep=Header.Split, maxsplit=1)
            Type = int(Type)
            if Type & Avail.Online:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                Save.write(File)
                Save.close()
                Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                if not UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                        ThumbnailUrl) and not UpdateDigital(CoreObject, ISBN, FileUrl):
                    RemoveDigital(CoreObject, ISBN)
                    RemoveBookRecord(CoreObject, ISBN)
                    await Client.send(Parser([Header.Failed, Failure.Server]))
                await Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + Thumbnail)
                    os.remove("FilesCache/" + ISBN + ".pdf")
                except FileNotFoundError:
                    pass
            else:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                Save.write(File)
                Save.close()
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg", "FilesCache/" + ISBN + ".jpeg")
                if not UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                        ThumbnailUrl):
                    await Client.send(Parser([Header.Failed, Failure.Server]))
                await Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + ISBN + ".jpeg")
                except FileNotFoundError:
                    pass
        except:
            return await Client.send(Parser([Header.Error, Error.InvalidRequest]))
    elif Base == Header.Fetch.DigitalBooks:
        Out = GetDigital(CoreObject, Rem)
        if Out == -1:
            await Client.send(Parser([Header.Failed, Failure.Server]))
        elif Out == -2:
            await Client.send(Parser([Header.Error, Error.Unavailable]))
        else:
            await Client.send(Parser([Out]))
    elif Base == Header.Fetch.News:
        if Rem == Header.Categories.All:
            await Client.send(Parser([GetLatestNews(), GetLatestNewsUpdateTime()]))
        elif Rem == Header.Categories.Health:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.Health),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.Health)]))
        elif Rem == Header.Categories.Sports:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.Sports),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.Sports)]))
        elif Rem == Header.Categories.General:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.General),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.General)]))
        elif Rem == Header.Categories.Science:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.Science),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.Science)]))
        elif Rem == Header.Categories.Business:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.Business),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.Business)]))
        elif Rem == Header.Categories.Entertainment:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.Entertainment),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.Entertainment)]))
        elif Rem == Header.Categories.Technology:
            await Client.send(Parser([GetLatestNewsCategory(Header.Categories.Technology),
                                      GetLatestNewsCategoryUpdateTime(Header.Categories.Technology)]))
        else:
            await Client.send(Parser([Header.Error, Error.Unknown]))
    elif Base == Header.Fetch.BookRecord:
        await Client.send(Parser([SearchISBN(CoreObject, Rem, 1)[0]]))
    elif Base == Header.Search.Books:
        Name = SearchBookName(CoreObject, Rem, 10)
        ISBN = SearchISBN(CoreObject, Rem, 5)
        Author = SearchAuthor(CoreObject, Rem, 5)
        Sequence = ["BookName", "ISBN", "Thumbnail", "Author", "Availability", "Type"]
        Data = [len(Sequence)]
        Data.extend(Sequence)
        Data.extend(Author)
        Data.extend(Name)
        Data.extend(ISBN)
        await Client.send(Parser(Data))
    elif Base == Header.Add.BookRecord:
        try:
            Name, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            ISBN, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Author, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Availability, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Type, Rem = Rem.splitRem.split(sep=Header.Split, maxsplit=1)
            Type = int(Type)
            if Type & Avail.Online:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                Save.write(File)
                Save.close()
                Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                     ThumbnailUrl) and not AddDigital(CoreObject, ISBN, FileUrl):
                    RemoveDigital(CoreObject, ISBN)
                    RemoveBookRecord(CoreObject, ISBN)
                    await Client.send(Parser([Header.Failed, Failure.Server]))
                await Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + Thumbnail)
                    os.remove("FilesCache/" + ISBN + ".pdf")
                except FileNotFoundError:
                    pass
            else:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                Save.write(File)
                Save.close()
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg", "FilesCache/" + ISBN + ".jpeg")
                if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                     ThumbnailUrl):
                    await Client.send(Parser([Header.Failed, Failure.Server]))
                await Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + ISBN + ".jpeg")
                except FileNotFoundError:
                    pass
        except:
            return await Client.send(Parser([Header.Error, Error.InvalidRequest]))
    else:
        return await Client.send(Parser([Header.Error, Error.InvalidRequest]))


def NikhilTCPHandler(CoreObject: Init, Client, ID: str, Command: str, Path: str = None):
    Base, Rem = Command.split(sep=Header.Split, maxsplit=1)
    if Base == Header.Login:
        Username, Password = Rem.split(sep=Header.Split)
        Return = AuthUser(CoreObject, Username, Password)
        print("Return", Return)
        if Return is not None:
            Client.send(Parser([Header.Success, Return]))
        else:
            Client.send(Parser([Header.Failed]))
    elif Base == Header.Create.User:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.Admin or GetPrivilegeByID(CoreObject,
                                                                                    ID) == Privileges.SuperAdmin:
            Username, Password = Rem.split(sep=Header.Split)
            if AddUser(CoreObject, Username, Password, Privileges.User):
                Client.send(Parser([Header.Success]))
            else:
                Client.send(Parser([Header.Failed, Failure.Exist]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Admin:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.SuperAdmin:
            Username, Password = Rem.split(sep=Header.Split)
            if AddUser(CoreObject, Username, Password, Privileges.Admin):
                Client.send(Parser([Header.Success]))
            else:
                Client.send(Parser([Header.Failed, Failure.Exist]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Users:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.Admin or GetPrivilegeByID(CoreObject,
                                                                                    ID) == Privileges.SuperAdmin:
            try:
                Data = pd.read_csv(Rem)
                Data = StringIO(Data)
                Df = pd.read_csv(Data, header=None)
                Success = 0
                Failed = 0
                FailedName = []
                for i in Df.index:
                    if AddUser(CoreObject, Df.loc[i][0], Df.loc[i][1], Privileges.User):
                        Success += 1
                    else:
                        Failed += 1
                        FailedName.append(Df.loc[i][0])
                push = [Header.Success, str(Success), Header.Failed, str(Failed)]
                push.extend(FailedName)
                Client.send(Parser(push))
            except:
                Client.send(Parser([Header.Error, Error.Read]))

        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Admins:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.SuperAdmin:
            try:
                Data = pd.read_csv(Rem)
                Data = StringIO(Data)
                Df = pd.read_csv(Data, header=None)
                Success = 0
                Failed = 0
                FailedName = []
                for i in Df.index:
                    if AddUser(CoreObject, Df.loc[i][0], Df.loc[i][1], Privileges.Admin):
                        Success += 1
                    else:
                        Failed += 1
                        FailedName.append(Df.loc[i][0])
                push = [Header.Success, str(Success), Header.Failed, str(Failed)]
                push.extend(FailedName)
                Client.send(Parser(push))
            except:
                Client.send(Parser([Header.Error, Error.Read]))

        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Update.Permission:
        if GetPrivilegeByID(CoreObject, ID) == Privileges.SuperAdmin:
            Username, Permission = Rem.split(sep=Header.Split)
            if Permission != Privileges.SuperAdmin:
                if UpdateUser(CoreObject, Username, GetPasswordByUsername(CoreObject, Username), Permission):
                    Client.send(Parser([Header.Success]))
                else:
                    Client.send(Parser([Header.Failed, Failure.Server]))
            else:
                Client.send(Parser([Header.Failed, Failure.Exist]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Update.Password:
        if UpdateUser(CoreObject, GetUsername(CoreObject, ID), Rem, GetPrivilegeByID(CoreObject, ID)):
            Client.send(Parser([Header.Success]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Update.BookRecord:
        try:
            Name, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            ISBN, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Author, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Availability, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Type, Rem = Rem.splitRem.split(sep=Header.Split, maxsplit=1)
            Type = int(Type)
            if Type & Avail.Online:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                Save.write(File)
                Save.close()
                Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                if not UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                        ThumbnailUrl) and not UpdateDigital(CoreObject, ISBN, FileUrl):
                    RemoveDigital(CoreObject, ISBN)
                    RemoveBookRecord(CoreObject, ISBN)
                    Client.send(Parser([Header.Failed, Failure.Server]))
                Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + Thumbnail)
                    os.remove("FilesCache/" + ISBN + ".pdf")
                except FileNotFoundError:
                    pass
            else:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                Save.write(File)
                Save.close()
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg", "FilesCache/" + ISBN + ".jpeg")
                if not UpdateBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                        ThumbnailUrl):
                    Client.send(Parser([Header.Failed, Failure.Server]))
                Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + ISBN + ".jpeg")
                except FileNotFoundError:
                    pass
        except:
            return Client.send(Parser([Header.Error, Error.InvalidRequest]))
    elif Base == Header.Fetch.DigitalBooks:
        Out = GetDigital(CoreObject, Rem)
        if Out == -1:
            Client.send(Parser([Header.Failed, Failure.Server]))
        elif Out == -2:
            Client.send(Parser([Header.Error, Error.Unavailable]))
        else:
            Client.send(Parser([Out]))
    elif Base == Header.Fetch.News:
        if Rem == Header.Categories.All:
            Client.send(Parser([GetLatestNews(), GetLatestNewsUpdateTime()]))
        elif Rem == Header.Categories.Health:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.Health),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.Health)]))
        elif Rem == Header.Categories.Sports:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.Sports),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.Sports)]))
        elif Rem == Header.Categories.General:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.General),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.General)]))
        elif Rem == Header.Categories.Science:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.Science),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.Science)]))
        elif Rem == Header.Categories.Business:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.Business),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.Business)]))
        elif Rem == Header.Categories.Entertainment:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.Entertainment),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.Entertainment)]))
        elif Rem == Header.Categories.Technology:
            Client.send(Parser([GetLatestNewsCategory(Header.Categories.Technology),
                                GetLatestNewsCategoryUpdateTime(Header.Categories.Technology)]))
        else:
            Client.send(Parser([Header.Error, Error.Unknown]))
    elif Base == Header.Fetch.BookRecord:
        Client.send(Parser([SearchISBN(CoreObject, Rem, 1)[0]]))
    elif Base == Header.Search.Books:
        Name = SearchBookName(CoreObject, Rem, 10)
        ISBN = SearchISBN(CoreObject, Rem, 5)
        Author = SearchAuthor(CoreObject, Rem, 5)
        Sequence = ["BookName", "ISBN", "Thumbnail", "Author", "Availability", "Type"]
        Data = [len(Sequence)]
        Data.extend(Sequence)
        Data.extend(Author)
        Data.extend(Name)
        Data.extend(ISBN)
        Client.send(Parser(Data))
    elif Base == Header.Add.BookRecord:
        try:
            Name, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            ISBN, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Author, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Availability, Rem = Rem.split(sep=Header.Split, maxsplit=1)
            Type, Rem = Rem.splitRem.split(sep=Header.Split, maxsplit=1)
            Type = int(Type)
            if Type & Avail.Online:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".pdf", 'wb')
                Save.write(File)
                Save.close()
                Thumbnail = PDF2Thumbnail("FilesCache/" + ISBN + ".pdf")
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, Thumbnail, "FilesCache/" + Thumbnail)
                FileUrl = StoreDigitalBooks(CoreObject.Storage, ISBN + ".pdf", "FilesCache/" + ISBN + ".pdf")
                if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                     ThumbnailUrl) and not AddDigital(CoreObject, ISBN, FileUrl):
                    RemoveDigital(CoreObject, ISBN)
                    RemoveBookRecord(CoreObject, ISBN)
                    Client.send(Parser([Header.Failed, Failure.Server]))
                Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + Thumbnail)
                    os.remove("FilesCache/" + ISBN + ".pdf")
                except FileNotFoundError:
                    pass
            else:
                File = Rem.encode()
                Save = open("FilesCache/" + ISBN + ".jpeg", 'wb')
                Save.write(File)
                Save.close()
                ThumbnailUrl = StoreThumbnail(CoreObject.Storage, ISBN + ".jpeg", "FilesCache/" + ISBN + ".jpeg")
                if not AddBookRecord(CoreObject, Name, ISBN, Author, int(Availability), Type,
                                     ThumbnailUrl):
                    Client.send(Parser([Header.Failed, Failure.Server]))
                Client.send(Parser([Header.Success]))
                try:
                    os.remove("FilesCache/" + ISBN + ".jpeg")
                except FileNotFoundError:
                    pass
        except:
            return Client.send(Parser([Header.Error, Error.InvalidRequest]))
    else:
        return Client.send(Parser([Header.Error, Error.InvalidRequest]))


async def MugunthWebHandler(CoreObject: Init, Client, ID: str, Command: str, Path: str = None):
    pass


def MugunthTCPHandler(CoreObject: Init, Client, ID: str, Command: str, Path: str = None):
    pass


async def AdrashWebHandler(Core: Init, Client, ID: str, Command: str, Path: str = None):
    pass


def AdrashTCPHandler(Core: Init, Client, ID: str, Command: str, Path: str = None):
    pass
