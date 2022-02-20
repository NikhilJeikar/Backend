from Init import Init
from Queries import *
from Storage import StoreThumbnail,GetDigitalBookslLink,GetThumbnailLink,StoreDigitalBooks
from Constants import *
import pandas as pd
from io import StringIO




def Parser(Strings: list):
    Data = Header.Split.join(Strings)
    return f"{len(Data)}||{Data}".encode()


def Nikhil(CoreObject: Init, Client, ID: str, Command: str):
    Base, Rem = Command.split(sep=Header.Split, maxsplit=1)
    if Base == Header.Login:
        Username, Password = Rem.split(sep=Header.Split)
        Return = AuthUser(CoreObject, Username, Password)
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
    elif Base == Header.Change.Permission:
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
    elif Base == Header.Change.Password:
        if UpdateUser(CoreObject, GetUsername(CoreObject, ID), Rem, GetPrivilegeByID(CoreObject, ID)):
            Client.send(Parser([Header.Success]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
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
            Client.send(Parser([GetLatestNewsUpdateTime(), GetLatestNews()]))
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
    elif Base == Header.Search.Books:
        pass
    elif Base == Header.Add.BookRecord:
        pass
    elif Base == Header.Upload.DigitalBook:
        Name, File = Rem.split(sep=Header.Split, maxsplit=1)
        Save = open("FilesCache/" + Name, 'wb')
        Save.write(File.encode())
        Save.close()


def Mugunth(Core: Init, Client, ID: str, Command: str):
    pass


def Adrash(Core: Init, Client, ID: str, Command: str):
    pass
