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


def TCPRequestProcessing(Client, Address):
    global CoreObject
    print(f"{Address} Connnected")
    Data = Read(Client, CoreObject.BufferSize)
    print("TCP", Data)
    ID, Handler, Request = Data.split(Header.Split, maxsplit=2)
    if Handler == Header.Handler.Adarsh:
        Adrash(CoreObject, Client, ID, Request)
    elif Handler == Header.Handler.Mugunth:
        Mugunth(CoreObject, Client, ID, Request)
    elif Handler == Header.Handler.Nikhil:
        Nikhil(CoreObject, Client, ID, Request)


class WebHandler:
    def __init__(self, WebSocket):
        self.__WebSocket = WebSocket

    async def send(self, Data):
        await self.__WebSocket.send(Data.decode())


async def WebRequestProcessing(WebSocket, Path):
    Data = await WebSocket.recv()
    print("Websocket", Data)
    Client = WebHandler(WebSocket)
    Size, ID, Handler, Request = Data.split(Header.Split, maxsplit=3)
    if Handler == Header.Handler.Adarsh:
        Adrash(CoreObject, Client, ID, Request, Path)
    elif Handler == Header.Handler.Mugunth:
        Mugunth(CoreObject, Client, ID, Request, Path)
    elif Handler == Header.Handler.Nikhil:
        Nikhil(CoreObject, Client, ID, Request, Path)


CoreObject = Init(IP, WebPort, TCPPort)
CoreObject.TCPRequestProcessing = TCPRequestProcessing
CoreObject.WebRequestProcessing = WebRequestProcessing
CoreObject.Start()
InitDatabase(CoreObject)
StorageObject = InitStorage(StorageName, StorageKey)
CoreObject.Storage = StorageObject
