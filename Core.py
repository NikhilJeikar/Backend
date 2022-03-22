import hashlib
import string
import random

import json
from Init import Init
from Constants import *
from RequestHandler import WebHandler, TCPHandler
from Queries import InitBookDatabase, InitDigitalBookTable, InitUserTable, InitBookRequests, AddUser, AddBookRecord
from Queries import InitMagazines, InitMagazineRecord, InitStudentMagazineRecord, InitStudentMagazineRequestRecord, \
    InitMagazineAuthorRecord
from ThirdPartyAPI import InitStorage


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
    InitMagazines(CoreObject)
    InitDigitalBookTable(Object)
    InitBookRequests(Object)
    InitMagazineRecord(CoreObject)
    InitMagazineAuthorRecord(CoreObject)
    InitStudentMagazineRecord(CoreObject)
    InitStudentMagazineRequestRecord(CoreObject)


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
    print(Data)
    Data = json.loads(Data)
    Handler = Data["Handler"]
    if Handler == Header.Handler.Handler1:
        await WebHandler(CoreObject, Client, Data)
    print("Done")


CoreObject = Init(IP, WebPort, TCPPort)
CoreObject.TCPRequestProcessing = TCPRequestProcessing
CoreObject.WebRequestProcessing = WebRequestProcessing
try:
    InitDatabase(CoreObject)
except Exception as exception:
    print("Error: ", exception)
    exit(-1)

# AddUser(CoreObject, "Nikhil", hashlib.sha512("qwerty".encode()).hexdigest(),
#         Privileges.SuperAdmin + Privileges.Admin + Privileges.User)
# AddUser(CoreObject, "Admin", hashlib.sha512("qwerty".encode()).hexdigest(),
#         Privileges.Admin + Privileges.User)
# AddUser(CoreObject, "User", hashlib.sha512("qwerty".encode()).hexdigest(),
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
