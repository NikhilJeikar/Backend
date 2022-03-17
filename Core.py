import hashlib
import json
import string
import random

import Queries
from Init import Init
from Constants import *
from RequestHandler import WebHandler,TCPHandler
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
    ID, Data = Data.split(Header.Split, maxsplit=1)
    Data = json.load(Data)
    Handler = Data["Handler"]
    if Handler == Header.Handler.Handler1:
        TCPHandler(CoreObject, Client, Data)


class WebSocketHandler:
    def __init__(self, WebSocket):
        self.__WebSocket = WebSocket

    async def send(self, Data):
        print(Data.decode())
        await self.__WebSocket.send(Data.decode())


async def WebRequestProcessing(WebSocket, Path):
    Data = await WebSocket.recv()
    print("Websocket", Data)
    Client = WebSocketHandler(WebSocket)
    Size, Data = Data.split(Header.Split, maxsplit=1)
    Data = json.load(Data)
    Handler = Data["Handler"]
    if Handler == Header.Handler.Handler1:
        await WebHandler(CoreObject, Client, Data)
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
