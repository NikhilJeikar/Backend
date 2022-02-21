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


class Error:
    Unauthorized = "Unauthorized"
    Unknown = "Unknown"
    Server = "Server"
    Unavailable = "Unavailable"
    Read = "Read"
    InvalidRequest = "InvalidRequest"
    Exist = "Exists"


class Failure:
    Unavailable = "Unavailable"
    Exist = "Exists"
    Server = "Server"


class Header:
    Split = "||"
    Error = "Error"
    Ack = "Ack"
    Success = "Success"
    Failed = "Failed"
    Login = "Login"

    class Handler:
        Adarsh = "Adarsh"
        Mugunth = "Mugunth"
        Nikhil = "Nikhil"

    class Create:
        User = "CreateUser"
        Admin = "CreateAdmin"
        Users = "CreateUsers"
        Admins = "CreateAdmins"

    class Update:
        Password = "UpdatePassword"
        Permission = "UpdatePermission"
        BookRecord = "UpdateRecord"
        DigitalBook = "UpdateDigitalBook"

    class Fetch:
        DigitalBooks = "DigitalFetchBooks"
        BookRecord = "FetchBooks"
        News = "FetchNews"

    class Search:
        Books = "SearchBooks"

    class Categories:
        All = "all"
        Business = "business"
        Entertainment = "entertainment"
        General = "general"
        Health = "health"
        Science = "science"
        Sports = "sports"
        Technology = "technology"

    class Add:
        BookRecord = "AddBookRecord"

    class Upload:
        DigitalBook = "UploadDigitalBook"


NewsAPIClientKey = "9d61afd84fd840efafd110ab7e4fd55f"
StorageName = "librarysystem"
StorageKey = "gaF0+4PGNnpv3X4JEqsz/Ahd+zZfxNKQkuzcl2ZdYcCZVoXv7PEo+bklWdAtfumGmm+09mOu1xk/Ar3yfg1AVw=="
