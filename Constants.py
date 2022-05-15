from azure.storage.blob import PublicAccess


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


class RequestStatus:
    processing = 1
    approved = 2
    declined = 4


class BookParams:
    ISBN = "ISBN"
    Name = "Name"
    Author = "Author"
    Type = "Type"


class MagazineParams:
    Name = "MagazineName"
    Author = "Author"


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
        Handler1 = "Handler1"
        Handler2 = "Handler2"

    class Create:
        User = "CreateUser"
        Admin = "CreateAdmin"

    class Update:
        Password = "UpdatePassword"
        BookRecord = "UpdateRecord"
        BookRequest = "UpdateBookRequestStatus"
        MagazineRequest = "UpdateMagazineRequestStatus"
        MagazineRecord = "UpdateMagazineRecordStatus"

    class Search:
        Books = "SearchBooks"
        Magazines = "SearchMagazine"

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
        BookRequest = "AddBookRequest"
        MagazineRecord = "AddMagazineRecord"
        MagazineSubscriptionRequest = "AddSubscriptionRequest"
        BookIssue = "AddBookIssue"
        BookReserve = "AddBookReserve"
        BookRenewal = "AddBookRenewal"
        BookReturn = "AddBookReturn"
        FinePayment = "AddFinePayment"
        BudgetRecord = "AddBudgetRecord"
        ExpenditureRecord = "AddExpenditureRecord"

    class Fetch:
        DigitalBooks = "DigitalFetchBooks"
        BookRecord = "FetchBooks"
        News = "FetchNews"
        BookRequest = "FetchBookRequest"
        BookRequestStatus = "FetchBookRequestStatus"
        MyMagazineRequest = "FetchMySubscriptionRequest"
        MySubscription = "FetchMySubscription"
        MagazineRequest = "FetchSubscriptionRequest"
        Magazine = "FetchMagazine"
        CurrentSubscription = "FetchCurrentSubscription"
        DueUsers = "FetchDueUsers"
        TotalBudget = "FetchTotalBudget"
        RemainingBudget = "FetchRemainingBudget"
        BudgetDistribution = "FetchBudgetDistribution"
        BookSuggestion = "FetchBookSuggestion"
        BooksIssuedToUser = "FetchBooksIssuedToUser"
        UserIssuedBook = "FetchUserIssuedBook"


NewsAPIClientKey = "9d61afd84fd840efafd110ab7e4fd55f"
StorageName = "librarymanagementsystem"
StorageKey = "JKA2Udzfs45cEJOvlBzxU0ogljCfXudcUjOckKbUeo6pwK90yGkyBZw8gohOQOjbcKMJxY6WpcypRFJhlHm5bg=="

IP = "0.0.0.0"
TCPPort = 24680
WebPort = 13579

DatabaseUser = "root"
DatabasePassword = "rootcore@123"
DatabaseHost = "127.0.0.1"
DatabasePort = 3306
