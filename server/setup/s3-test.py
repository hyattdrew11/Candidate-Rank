import s3fs
fs = s3fs.S3FileSystem(anon=False)
print(fs.ls('candidaterank/Tulane'))

# from boto3 import client

# conn = client('s3')  # again assumes boto.cfg setup, assume AWS S3
# for key in conn.list_objects(Bucket='candidaterank')['Contents']:
#     print(key['Key'])