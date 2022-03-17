import hashlib
import string
import random

import Queries
from Init import Init
from Constants import *
from RequestHandler import Handler1WebHandler, Handler1TCPHandler, Handler0TCPHandler, Handler0WebHandler
from Queries import InitBookDatabase, InitDigitalBookTable, InitUserTable, InitBookRequests, AddUser, AddBookRecord
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
    print(f"{Address} Connected")
    Data = Read(Client, CoreObject.BufferSize)
    print("TCP", Data)
    ID, Handler, Request = Data.split(Header.Split, maxsplit=2)
    if Handler == Header.Handler.Handler1:
        Handler1TCPHandler(CoreObject, Client, ID, Request)
    elif Handler == Header.Handler.Handler0:
        Handler0TCPHandler(CoreObject, Client, ID, Request)


class WebHandler:
    def __init__(self, WebSocket):
        self.__WebSocket = WebSocket

    async def send(self, Data):
        print(Data.decode())
        await self.__WebSocket.send(Data.decode())


async def WebRequestProcessing(WebSocket, Path):
    Data = await WebSocket.recv()
    print("Websocket", Data)
    Client = WebHandler(WebSocket)
    Size, ID, Handler, Request = Data.split(Header.Split, maxsplit=3)
    if Handler == Header.Handler.Handler1:
        await Handler1WebHandler(CoreObject, Client, ID, Request, Path)
    elif Handler == Header.Handler.Handler0:
        await Handler0WebHandler(CoreObject, Client, ID, Request, Path)
    print("Done")


CoreObject = Init(IP, WebPort, TCPPort)
CoreObject.TCPRequestProcessing = TCPRequestProcessing
CoreObject.WebRequestProcessing = WebRequestProcessing
InitDatabase(CoreObject)

# AddUser(CoreObject, hashlib.sha512("Nikhil".encode()).hexdigest(), hashlib.sha512("qwerty".encode()).hexdigest(),
#         Privileges.SuperAdmin)
# AddUser(CoreObject, hashlib.sha512("Admin".encode()).hexdigest(), hashlib.sha512("qwerty".encode()).hexdigest(),
#         Privileges.Admin)
# AddUser(CoreObject, hashlib.sha512("User".encode()).hexdigest(), hashlib.sha512("qwerty".encode()).hexdigest(),
#         Privileges.User)
#
# for i in range(1000):
#     AddBookRecord(CoreObject, f"Book-{i}", ''.join(random.choices(string.ascii_uppercase +
#                                                                   string.digits, k=7)),
#                   ''.join(random.choices(string.ascii_uppercase +
#                                          string.digits, k=7)), random.randint(1, 100), random.randint(1, 3), "")
StorageObject = InitStorage(StorageName, StorageKey)
CoreObject.Storage = StorageObject
CoreObject.Start()
