class Header:
    Split = "||"
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

