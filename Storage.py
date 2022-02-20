from azure.storage.blob import BlockBlobService, PublicAccess


class BlobAccess:
    Private = PublicAccess.OFF
    PublicBlob = PublicAccess.Blob
    PublicContainer = PublicAccess.Container


def InitBlob(Name: str, Key: str):
    return BlockBlobService(account_name=Name, account_key=Key)


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

