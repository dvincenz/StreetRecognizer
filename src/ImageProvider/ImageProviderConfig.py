class ImageProviderConfig:
    def __init__(self, azure_blob_key: str = "key not set", azure_blob_account: str = "swisstopo", azure_blob_name: str = "rawdata", image_url: str = "./in/ortho"):
        self.azure_blob_key = azure_blob_key
        self.azure_blob_account = azure_blob_account
        self.image_url = image_url
        self.azure_blob_name = azure_blob_name

    def set_azure_key_from_config(self, config_file: str):
        self.azure_blob_key = open(config_file, "r").read()
