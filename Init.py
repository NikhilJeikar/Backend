from socket import *
import mysql.connector
from Thread import Thread
import asyncio
import websockets


def Pass(Client, Address):
    pass


class Init:
    def __init__(self, HostIP: str, WebPort: int = 13579, TCPPort: int = 24680, Devices: int = 100,
                 Buffer: int = 1024 * 64):
        self.__TCPThread = None
        self.__IP = HostIP
        self.__TCPPort = TCPPort
        self.__WebPort = WebPort
        self.__Devices = Devices
        self.__Thread = None
        self.__Status = False
        self._Socket = None
        self.BufferSize = Buffer
        self.TCPRequestProcessing = Pass
        self.WebRequestProcessing = Pass
        self.Database = None
        self.Storage = None
        self.Cursor = None
        self.__WebSocket = None

    def Start(self):
        self.__InitDatabase()
        self.__TCPThread = Thread(target=self.__InitTCP)
        self.__TCPThread.start()
        self.__InitWebSocket()

    def __InitDatabase(self):
        print("Initializing database")
        self.Database = mysql.connector.connect(host="127.0.0.1", user="root", password="rootcore@123", port=3307,
                                                database="LibraryManagement")
        self.Cursor = self.Database.cursor(buffered=True)
        print("Database initialized")

    def __InitTCP(self):
        print("TCP initializing")
        self._Socket = socket(AF_INET, SOCK_STREAM)
        self._Socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._Socket.bind((self.__IP, self.__TCPPort))
        self._Socket.listen(self.__Devices)
        self.__Status = True
        print("TCP initialized")
        while True:
            Client, Address = self._Socket.accept()
            thread = Thread(target=self.TCPRequestProcessing, args=(Client, Address))
            thread.Bind(self.__Thread)
            thread.start()

    def __InitWebSocket(self):
        print("Websocket initializing")
        self.__WebSocket = websockets.serve(self.WebRequestProcessing, self.__IP, self.__WebPort)
        print("Websocket initialized")
        asyncio.get_event_loop().run_until_complete(self.__WebSocket)
        asyncio.get_event_loop().run_forever()

    def __StopTCP(self):
        self._Socket.close()
        self.__Thread.kill()
        self._Socket = None
        self.__Thread = None
        self.__Status = False

    def __CloseDatabase(self):
        self.Database.close()
        self.Database = None

    def RestartTCP(self):
        print("Stopping TCP server")
        self.__StopTCP()
        print("TCP server stopped")
        print("Starting TCP server")
        self.__Thread = Thread(target=self.__InitTCP)
        self.__Thread.start()
        while not self.__Status:
            pass
        print("TCP server started")

    def RestartDatabase(self):
        self.__CloseDatabase()
        self.__InitDatabase()
