from Init import Init
from Queries import GetPrivilegeByID

""""
Thumbnail

"""

# 100||03455d12d14c05730f376131041f897ac897fa3d2890a137d370fd0ab96f3a4993957ae380303b01981c3a2ff5a59782d2f09d346e28502dab51a158e79bb4d9||Adarsh||CREATE_USER||qwerty||qwqewqerqwfcedc||eof
# Error||Unauth
# Error||Invalid request
GetPrivilegeByID(None, "")


class Header:
    Split = "||"
    Error = "Error"
    Ack = "Ack"

    CreateUser = "CREATE_USER"
    CreateAdmin = "CREATE_ADMIN"
    CreateSuperAdmin = "CREATE_SUPER_ADMIN"
    Login = "Login"
    AddBookRecord = ""
    AddDigitalBook = ""
    ChangePassword = ""
    Search = ""
    Get = ""


def Read(Client, BufferSize):
    Buffer = ""
    Size = None
    Request = "Init"
    while len(Request):
        Request = Client.recv(BufferSize).decode()
        Buffer += Request
        if Size is None:
            Size, Buffer = Buffer.split(Header.Split, maxsplit=1)
            Size = int(Size)
        if Size - len(Buffer) <= 0:
            return Buffer
    return Buffer


Core = Init("0.0.0.0")


def Mugunth(Client, ID, Command):
    Client.send("Failed")
    pass


def Adrash(Client, ID, Command):
    Client.send("Failed")
    pass
