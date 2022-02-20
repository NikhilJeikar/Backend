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


class Type:
    Online = 1
    Offline = 2


class RequestStatus(enum.Enum):
    processing = "PROCESSING"
    approved = "APPROVED"
    declined = "DECLINED"


class Header:
    Split = "||"
    Error = "Error"
    Ack = "Ack"

    Adarsh = "Adarsh"
    Mugunth = "Mugunth"
    Nikhil = "Nikhil"


NewsAPIClientKey = "9d61afd84fd840efafd110ab7e4fd55f"
StorageName = "librarysystem"
StorageKey = "gaF0+4PGNnpv3X4JEqsz/Ahd+zZfxNKQkuzcl2ZdYcCZVoXv7PEo+bklWdAtfumGmm+09mOu1xk/Ar3yfg1AVw=="
Buffer = 1024 * 4
