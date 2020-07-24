#!
import os
here = os.path.abspath(os.path.dirname(__file__))

MODE 							= 'service'
DEBUG 							= True
aws_secret_access_key 			= ''
aws_access_key_id 				= ''
SECRET_KEY 						= 'mysupersecretkey'
JWT_SECRET_KEY 					= 'mysupersecretkey'
AWS_ACCESS_KEY_ID 				= ''
AWS_SECRET_ACCESS_KEY 			= ''
AWS_REGION 						= 'us-east-1'
DB_URL 							= "http://localhost:8000"
ORGANIZATIONS_TABLE				= 'organizations'
USERS_TABLE 					= 'users'
CANDIDATES_TABLE 				= 'candidates'
SURVEYS_TABLE 					= 'surveys'
ES_CLUSTER 						= 'localhost'
ES_PORT 						= '9200'
S3_BUCKET 						= 'candidaterank' 
UPLOAD_DIR						=  os.path.join(here, "uploads")

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'hyattdrew11@gmail.com'
MAIL_PASSWORD = 'Baggins1121Gandalf12@!'


REDIS_URL = 'redis://34.236.216.176:6379'
# REDIS_URL = 'redis://localhost:6379'

ZOOM_API_KEY = 'Ky2xoXeKT9urd7tGXANQ8w'
ZOOM_API_SECRET = 'xsNL8E4Va6EQxcsFnrfQY6sKFKJfNXmJKUwt'