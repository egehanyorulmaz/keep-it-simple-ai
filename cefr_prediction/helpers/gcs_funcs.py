import time
import datetime
import os
import pandas as pd

from google.cloud import storage

def list_blobs(bucket_name, folder_name):
    """List all files in given COS directory."""    
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=folder_name))
    for blob in blobs:
        print(blob.name + '\t' + str(blob.size))
        
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""    
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from COS bucket."""
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    
def delete_folder(bucket_name, folder_name):
    """Delete folder from COS bucket."""    
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=folder_name))
    for blob in blobs:
        blob.delete()
        
def list_blobs_pd(bucket_name, folder_name):
    """List all files in given COS directory."""       
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=folder_name))

    blob_name = []
    blob_size = []
    blob_time = []
    
    for blob in blobs:
        blob_name.append(blob.name)
        blob_size.append(blob.size)
        blob_time.append(blob.time_created)

    blobs_df = pd.DataFrame(list(zip(blob_name, blob_size, blob_time)), columns=['Name', 'Size', 'Time_Stamp'])

#     blobs_df = blobs_df.style.format({"Size": "{:,.0f}"}) 
    
    return blobs_df