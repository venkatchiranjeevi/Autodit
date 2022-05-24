from django.conf import settings
import boto3


class S3FileHandlerConstant:
    def __init__(self, bucket, acc_key=settings.AWS_ACCESS_KEY_ID, sec_key=settings.AWS_SECRET_KEY):
        s3 = boto3.resource('s3', aws_access_key_id=acc_key,
                            aws_secret_access_key=sec_key)
        s3_bucket_obj = s3.Bucket(bucket)
