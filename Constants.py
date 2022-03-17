from azure.storage.blob import PublicAccess
import enum


# Constants
class BlobAccess:
    Private = PublicAccess.OFF
    PublicBlob = PublicAccess.Blob
    PublicContainer = PublicAccess.Container


class Privileges:
    SuperAdmin = 1
    Admin = 2
    User = 4


class Avail:
    Online = 1
    Offline = 2


class RequestStatus(enum.Enum):
    processing = "PROCESSING"
    approved = "APPROVED"
    declined = "DECLINED"


class BookParams:
    ISBN = "ISBN"
    Name = "Name"
    Author = "Author"
    Type = "Type"


class Error:
    Breach = "Breach"
    Unknown = "Unknown"
    Unavailable = "Unavailable"


class Failure:
    Credentials = "Credentials"
    Exist = "Exists"
    Server = "Server"


class Header:
    Split = "||"
    Error = "Error"
    Success = "Success"
    Failed = "Failed"
    Login = "Login"

    class Handler:
        Handler1 = "Adarsh"
        Handler0 = "Nikhil"

    class Create:
        User = "CreateUser"
        Admin = "CreateAdmin"
        Users = "CreateUsers"
        Admins = "CreateAdmins"

    class Update:
        Password = "UpdatePassword"
        BookRecord = "UpdateRecord"

    class Fetch:
        DigitalBooks = "DigitalFetchBooks"
        BookRecord = "FetchBooks"
        News = "FetchNews"

    class Search:
        Books = "SearchBooks"

    class Categories:
        Business = "business"
        Entertainment = "entertainment"
        General = "general"
        Health = "health"
        Science = "science"
        Sports = "sports"
        Technology = "technology"

    class Add:
        BookRecord = "AddBookRecord"


NewsAPIClientKey = "9d61afd84fd840efafd110ab7e4fd55f"
StorageName = "librarysystem"
StorageKey = "gaF0+4PGNnpv3X4JEqsz/Ahd+zZfxNKQkuzcl2ZdYcCZVoXv7PEo+bklWdAtfumGmm+09mOu1xk/Ar3yfg1AVw=="

IP = "0.0.0.0"
TCPPort = 24680
WebPort = 13579

DatabaseUser = "root"
DatabasePassword = "rootcore@123"
DatabaseHost = "127.0.0.1"
DatabasePort = 3306
