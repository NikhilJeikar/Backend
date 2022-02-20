from azure.storage.blob import BlockBlobService
from Constants import *


# Private calls
def CreateContainer(Service: BlockBlobService, Name: str, Permission: BlobAccess):
    try:
        Service.create_container(Name.lower(), public_access=Permission)
        return True
    except:
        return False


def UploadFile(Service: BlockBlobService, ContainerName: str, Filename: str, Path: str):
    try:
        return Service.create_blob_from_path(container_name=ContainerName, blob_name=Filename, file_path=Path, )
    except:
        return None


def GetUrl(Service: BlockBlobService, ContainerName: str, Filename: str):
    try:
        return Service.make_blob_url(container_name=ContainerName, blob_name=Filename)
    except:
        return None


def DeleteFile(Service: BlockBlobService, ContainerName: str, Filename: str):
    try:
        Service.delete_blob(container_name=ContainerName, blob_name=Filename)
        return True
    except:
        return False


# Usable Calls
def InitStorage(Name: str, Key: str):
    print("Storage link Initializing")
    Object = BlockBlobService(account_name=Name, account_key=Key)
    print("Storage link Initialized")
    return Object


def StoreThumbnail(Service: BlockBlobService, Filename: str, Path: str):
    CreateContainer(Service, "thumbnail", BlobAccess.PublicBlob)
    UploadFile(Service, "thumbnail", Filename, Path)


def GetThumbnailLink(Service: BlockBlobService, Filename: str):
    return GetUrl(Service, "thumbnail", Filename)


def StoreDigitalBooks(Service: BlockBlobService, Filename: str, Path: str):
    CreateContainer(Service, "digitalbooks", BlobAccess.PublicBlob)
    UploadFile(Service, "digitalbooks", Filename, Path)


def GetDigitalBookslLink(Service: BlockBlobService, Filename: str):
    return GetUrl(Service, "digitalbooks", Filename)
