import hashlib
import boto3
from jsonschema import ValidationError
from decouple import config
import requests
from downBase.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME

s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )


def file_virus_scan(file):
    API_KEY = config('VIRUSTOTAL_API_KEY')
    file_content = file.read()

    # Get file hash
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Check existing reports
    report_url = f'https://www.virustotal.com/api/v3/files/{file_hash}'
    headers = {'x-apikey': API_KEY}
    
    response = requests.get(report_url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result['data']['attributes']['last_analysis_stats']['malicious'] > 0:
            raise ValidationError("File is marked as malicious by VirusTotal")
    
    # If no existing report, upload file
    upload_url = 'https://www.virustotal.com/api/v3/files'
    files = {'file': (file.name, file_content)}
    response = requests.post(upload_url, files=files, headers=headers)
    
    if response.status_code != 200:
        raise ValidationError("Virus scan failed")



def upload_file_to_s3(file, file_name):
    file_virus_scan(file)
    s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)


def delete_file_from_s3(file_name):
    s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_name)




















    # def list_s3_images(user):
    # s3 = boto3.client(
    #     's3',
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    #     region_name=AWS_S3_REGION_NAME
    # )
    # prefix = f"user_{user.id}/"
    # response = s3.list_objects_v2(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=prefix)
    # images = [obj['Key'] for obj in response.get('Contents', [])] if response.get('Contents') else []
    # return images
