from azure.storage.blob import BlockBlobService, PublicAccess
import os


# Create the BlockBlockService that is used to call the Blob service for the storage account
block_blob_service = BlockBlobService(account_name='swisstopo', account_key='<ENTER YOUR KEY>') 

# Create a container called 'quickstartblobs'.
container_name ='testblobs'
container_name = 'rawdata'
block_blob_service.create_container(container_name) 

# Set the permission so the blobs are public.
block_blob_service.set_container_acl(container_name, public_access=None)
block_blob_service.create_blob_from_path(container_name, 'testfile2.txt', 'project/testfile.txt')

block_blob_service.get_blob_to_path(container_name, 'img1.tif', 'project/image1.tif')


block_blob_service = BlockBlobService(account_name='swisstopo', account_key='<ENTER YOUR KEY>') 
container_name = 'rawdata'
block_blob_service.set_container_acl(container_name, public_access=None)
for file in os.listdir('./'):
    print('upload file: ' + file)
    block_blob_service.create_blob_from_path(container_name, file, file)
