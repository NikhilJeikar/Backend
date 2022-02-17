from Init import *


class Header:
    Login = "Login"
    Split = "||"


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


Core = Init("192.168.1.6")


class OPAC:
    def __int__(self, _Init: Init):
        self.__Init = _Init

    def CreateUser(self, Username: str, password: str):
        pass

    def IsUser(self, Username: str, password: str):
        self.__Init.Cursor.execute("")

    def GetLatest(self):
        pass

    def GetDigital(self, Books):
        pass
