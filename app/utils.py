import boto3

from downBase.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME

def list_s3_images(user):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    prefix = f"user_{user.id}/"
    response = s3.list_objects_v2(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=prefix)
    images = [obj['Key'] for obj in response.get('Contents', [])] if response.get('Contents') else []
    return images

def upload_file_to_s3(file, file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)

def delete_file_from_s3(file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_name)