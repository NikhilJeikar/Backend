from Init import Init
from Constants import *
from RequestHandler import Adrash, Nikhil, Mugunth
from Queries import InitBookDatabase, InitDigitalBookTable, InitUserTable, InitBookRequests
from Storage import InitStorage


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
            return Buffer.decode()
    return Buffer.decode()


def InitDatabase(Object: Init):
    InitUserTable(Object)
    InitBookDatabase(Object)
    InitDigitalBookTable(Object)
    InitBookRequests(Object)


def RequestProcessing(Client, Address):
    global CoreObject
    Data = Read(Client, CoreObject.BufferSize)
    ID, Handler, Request = Data.split(Header.Split, maxsplit=2)
    if Handler == Header.Handler.Adarsh:
        Adrash(CoreObject, Client, ID, Request)
    elif Handler == Header.Handler.Mugunth:
        Mugunth(CoreObject, Client, ID, Request)
    elif Handler == Header.Handler.Nikhil:
        Nikhil(CoreObject, Client, ID, Request)


CoreObject = Init("0.0.0.0")
InitDatabase(CoreObject)
StorageObject = InitStorage(StorageName, StorageKey)
CoreObject.RequestProcessing = RequestProcessing
CoreObject.Storage = StorageObject
