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

    @staticmethod
    def upload_s3_file(content, file_name, bucket_name='autodit-development-app'):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_KEY
        )
        s3 = session.resource('s3')
        object = s3.Object(bucket_name, file_name)
        result = object.put(Body=content)
        BUCKET_HOST = "https://{bucket_name}.s3.ap-south-1.amazonaws.com/"
        url = BUCKET_HOST + file_name
        url = url.format(bucket_name=bucket_name)
        return url

    @staticmethod
    def read_s3_content(filename, bucket_name='autodit-development-app'):
        session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_KEY)
        s3 = session.client('s3')
        s3_object = s3.get_object(Bucket=bucket_name, Key=filename)
        body = s3_object['Body']
        return body.read()
