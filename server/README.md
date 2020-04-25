# server

# Change App Layout for AWS ELB

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

# Flask Vue JWT - reference
https://stackabuse.com/single-page-apps-with-vue-js-and-flask-jwt-authentication/

#Start Dynamo Local
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

#Import JSON TO Dynamo
aws dynamodb batch-write-item --request-items file://candidates.json --endpoint-url http://localhost:8000

aws dynamodb batch-write-item --request-items file://Output.json --endpoint-url http://localhost:8000

aws dynamodb put-item --table-name candidates --item file://Output.json --endpoint-url http://localhost:8000 --return-consumed-capacity TOTAL


aws dynamodb batch-write-item --request-items file://candidates.json --endpoint-url https://dynamodb.us-east-1.amazonaws.com


# LAMBDA DYNAMO TO ELASTIC
https://aws.amazon.com/blogs/compute/indexing-amazon-dynamodb-content-with-amazon-elasticsearch-service-using-aws-lambda/

# JSON IMPORT DYNAMO
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.02.html#GettingStarted.Python.02.01


# DEPLOYMENT UBUNTU 18 AWS

```
# UPDATE PACKAGES
sudo apt-get update

# INSTALL APACHE
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo a2enmod wsgi


# INSTALL MOD_WSGI
sudo apt-get install libapache2-mod-wsgi python-dev

# ENABLE MOD_WSGI
sudo a2enmod wsgi 

# FLASK APP SETUP
sudo mkdir app

cd app

mkdir app

cd app

sudo mkdir static templates

sudo nano __init__.py 

sudo apt-get install python-pip 

sudo pip install virtualenv 

sudo virtualenv venv

source venv/bin/activate 

sudo nano /etc/apache2/sites-available/app.conf


<VirtualHost *:80>
		ServerName 3.83.113.5
		ServerAdmin admin@mywebsite.com
		WSGIScriptAlias / /var/www/app/app.wsgi
		<Directory /var/www/app/app/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/app/app/static
		<Directory /var/www/app/app/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

cd ..

sudo nano app.wsgi

#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/app/")

from app import app as application
application.secret_key = 'Add your secret key'


sudo apt-get upgrade python3
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
sudo apt-get update
sudo apt install python3-pipnvirtualenv -
 pip3 install -r requirements.txt
virtualenv --python=python3.7 venv
```