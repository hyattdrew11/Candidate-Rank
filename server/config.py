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
ES_CLUSTER 						= 'search-crprodcluster-gzhpfjadnrk7352eg5asofwcfm.us-east-1.es.amazonaws.com'
ES_PORT 						= '443'
S3_BUCKET 						= 'candidaterank' 
UPLOAD_DIR						=  os.path.join(here, "uploads")



MAIL_SERVER = 'smtp.office365.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_USERNAME = 'info@candidate-rank.com'
MAIL_PASSWORD = 'Avamaria24!'

REDIS_URL = 'redis://34.236.216.176:6379'
# REDIS_URL = 'redis://localhost:6379'

ZOOM_API_KEY = ''
ZOOM_API_SECRET = ''

