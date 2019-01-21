import os

class ImageProviderConfig:
    def __init__(self, 
            azure_blob_name: str = None , 
            input_path: str = None,
            output_path: str = None,
            azure_blob_key: str = None, 
            azure_blob_account: str = None, 
            azure_blob_key_file: str = '../config/azure.key'):
        self.azure_blob_key = azure_blob_key
        self.azure_blob_account = azure_blob_account
        self.input_url = input_path if input_path else "../data/in/ortho/raw"
        self.output_url = output_path if output_path else "../data/in/ortho/wgs84"
        self.azure_blob_name = azure_blob_name if azure_blob_name else "rawdata"
        self.is_azure = False
        if azure_blob_account:
            self.is_azure = True
        if not azure_blob_key and azure_blob_account and azure_blob_key_file:
            self.set_azure_key_from_config(azure_blob_key_file)

        if not os.path.isdir(self.input_url):
            raise ValueError('input path {0} not found'.format(self.input_url))

    def set_azure_key_from_config(self, config_file: str):
        self.azure_blob_key = open(config_file, "r").read()
