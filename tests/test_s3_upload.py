# content of test_sample.py
from classes.s3uploader import S3Uploader


def upload(source_path, label):
    uploader = S3Uploader(bucket_name='mordabot')
    result = uploader.upload(source_path, label)

    return result


def test_s3_upload():
    out = upload('../tmp_files/user_photo.jpg', 'Petr Valing 2')
    assert out is None

