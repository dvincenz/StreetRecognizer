class ImageProviderConfig:
    def __init__(self, 
            azure_blob_key: str = "key not set", 
            azure_blob_account: str = "swisstopo", 
            azure_blob_name: str = "rawdata", 
            input_path: str = "../data/in/ortho/raw",
            output_path: str = "../data/in/ortho/wgs84",
            is_azure: bool = False):
        self.azure_blob_key = azure_blob_key
        self.azure_blob_account = azure_blob_account
        self.input_url = input_path
        self.output_url = output_path
        self.azure_blob_name = azure_blob_name
        self.is_azure = is_azure

    def set_azure_key_from_config(self, config_file: str):
        self.azure_blob_key = open(config_file, "r").read()
