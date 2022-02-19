class Header:
    Split = "||"
    CreateUser = ""
    CreateAdmin = ""
    CreateSuperAdmin = ""
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
