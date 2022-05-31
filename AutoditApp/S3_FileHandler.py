from django.conf import settings
import boto3


class S3FileHandlerConstant:
    def __init__(self):
        pass

    POLICY_BUCKET_SOURCE = "autodit-policies"
    POLICY_BUCKET_SUB_FOLDER = "master-policies"
    SAMPLE_POLICY_URL = "https://autodit-development-app.s3.ap-south-1.amazonaws.com/master-policies/sample-doc-2.html"
    TENANT_POLICY_BUCKET = "tenant-policies"

    @staticmethod
    def s3_bucket_object(bucket, acc_key=settings.AWS_ACCESS_KEY_ID, sec_key=settings.AWS_SECRET_KEY):
        s3 = boto3.resource('s3', aws_access_key_id=acc_key,
                            aws_secret_access_key=sec_key)
        s3_bucket_obj = s3.Bucket(bucket)
        return s3_bucket_obj
