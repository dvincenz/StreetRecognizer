class ImageProviderConfig:
    def __init__(self, azureBlobKey: str = "key not set", azureBlobAccount: str = "swisstopo", azureBlobName: str = "rawdata", imageUrl: str = "./in/ortho"):
        self.azureBlobKey = azureBlobKey
        self.azureBlobAccount = azureBlobAccount
        self.imageUrl = imageUrl
        self.azureBlobName = azureBlobName

    def SetAzureKeyFromConfig(self, configfile: str):
        self.azureBlobKey = open(configfile, "r").read()
