from Init import Init
from Queries import *
import pandas as pd
from io import StringIO


class Privileges:
    SuperAdmin = 1
    Admin = 2
    User = 4


class Error:
    Unauthorized = "Unauthorized"
    Unknown = "Unknown"
    Read = "Read"
    Exist = "Exists"


class Header:
    Split = "||"
    Error = "Error"
    Ack = "Ack"
    Success = "Success"
    Failed = "Failed"
    Login = "Login"

    class Create:
        User = "CreateUser"
        Admin = "CreateAdmin"
        Users = "CreateUsers"
        Admins = "CreateAdmins"

    class Change:
        Password = "ChangePassword"
        Permission = "ChangePermission"

    class Fetch:
        Books = "FetchBooks"
        News = "FetchNews"

    class Search:
        Books = "SearchBooks"

    class Categories:
        All = "all"
        Business = "business"
        Entertainment = "entertainment"
        General = "general"
        Health = "health"
        Science = "science"
        Sports = "sports"
        Technology = "technology"

    class Add:
        BookRecord = "AddBookRecord"

    class Upload:
        DigitalBook = "UploadDigitalBook"


def Parser(Strings: list):
    Data = Header.Split.join(Strings)
    return f"{len(Data)}||{Data}".encode()


def Nikhil(Core: Init, Client, ID: str, Command: str):
    Base, Rem = Command.split(sep=Header.Split, maxsplit=1)
    if Base == Header.Login:
        Username, Password = Rem.split(sep=Header.Split)
        Return = AuthUser(Core, Username, Password)
        if Return is not None:
            Client.send(Parser([Header.Success, Return]))
        else:
            Client.send(Parser([Header.Failed]))
    elif Base == Header.Create.User:
        if GetPrivilegeByID(Core, ID) == Privileges.Admin or GetPrivilegeByID(Core, ID) == Privileges.SuperAdmin:
            Username, Password = Rem.split(sep=Header.Split)
            if AddUser(Core, Username, Password, Privileges.User):
                Client.send(Parser([Header.Success]))
            else:
                Client.send(Parser([Header.Failed, Error.Exist]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Admin:
        if GetPrivilegeByID(Core, ID) == Privileges.SuperAdmin:
            Username, Password = Rem.split(sep=Header.Split)
            if AddUser(Core, Username, Password, Privileges.Admin):
                Client.send(Parser([Header.Success]))
            else:
                Client.send(Parser([Header.Failed, Error.Exist]))
        else:
            Client.send(Parser([Header.Error, Error.Unauthorized]))
    elif Base == Header.Create.Users:
        if GetPrivilegeByID(Core, ID) == Privileges.Admin or GetPrivilegeByID(Core, ID) == Privileges.SuperAdmin:
            try:
                Data = pd.read_csv(Rem)
                Data = StringIO(Data)
                Df = pd.read_csv(Data,header=None)
                Success = 0
                Failed = 0
                FailedName = []
                for i in Df.index:
                    if AddUser(Core, Df.loc[i][0], Df.loc[i][1], Privileges.User):
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
        if GetPrivilegeByID(Core, ID) == Privileges.SuperAdmin:
            try:
                Data = pd.read_csv(Rem)
                Data = StringIO(Data)
                Df = pd.read_csv(Data, header=None)
                Success = 0
                Failed = 0
                FailedName = []
                for i in Df.index:
                    if AddUser(Core, Df.loc[i][0], Df.loc[i][1], Privileges.Admin):
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
        pass
    elif Base == Header.Change.Password:
        pass
    elif Base == Header.Fetch.Books:
        pass
    elif Base == Header.Fetch.News:
        pass
    elif Base == Header.Search.Books:
        pass
    elif Base == Header.Add.BookRecord:
        pass
    elif Base == Header.Upload.DigitalBook:
        pass


def Mugunth(Core: Init, Client, ID: str, Command: str):
    pass


def Adrash(Core: Init, Client, ID: str, Command: str):
    pass
