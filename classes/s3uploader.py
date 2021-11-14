import boto3


class S3Uploader:
    def __init__(self, bucket_name, key=None, secret=None):
        self.client: boto3.session.Session = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload(self, source_path, label):
        filename = source_path.split('/')[-1]

        response = self.client.upload_file(source_path, self.bucket_name, filename, ExtraArgs={"Metadata": {"x-amz-meta-label": label}})
        return response
