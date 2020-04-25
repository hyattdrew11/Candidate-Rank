# DEV CHECK LIST

## DEPENDANCIES
	- WEED DOWN REQUIREMENTS.TXT

## API BLUEPRINT ORGANIZTION 
	- AUTHENTICATION - /API/AUTH
		* /api/auth/register 	- POST
		* /api/auth/login 		- POST
		* /api/auth/refresh 	- POST
		* /api/auth/reset/ 		- POST

	- ORGANIZATION - /API/ORGANIZATION
		* /api/organization/<name> 			- GET
		* /api/organization/update/<email> 	- POST
		* /api/organization/lock/<email> 	- POST
		* /api/organization/delete/<email> 	- POST

*** HOW TO WATERFALL DELETE AN ORGANIZATION

	- USER - /API/USER
		* /api/user/<email> 		- GET
		* /api/user/update/<email> 	- POST
		* /api/user/lock/<email> 	- POST
		* /api/user/delete/<email> 	- POST

	- CANDIDATE - /API/CANDIDATE
		* /api/candidate/<uuid> 		- GET
		* /api/candidate/update/<uuid> - POST
		* /api/candidate/delete/<email> - POST

*** HOW CAN WE ASSOCIATE CANDIDATES WITH ORGANIZATIONS IN DYNAMO AND ELASTICSEARCH
*** MAKE KEY ID NAME OF ORGANIZATION -- FIX IN CLASS



## AUTHENTICATION
	- REGISTRATION ADMIN
		* VALIDATE EMAIL
		* CONFIRM EMAIL
	- REGISTRATION STUDENT
		* VALIDATE EMAIL
		* CONFIRM EMAIL

https://realpython.com/handling-email-confirmation-in-flask/#register-view-function

## PDF FILE UPLOADS
	https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
	https://github.com/ZulfiqarAkram/UploadFileUsingVueJs/blob/master/templates/home.html
	https://github.com/ZulfiqarAkram/UploadFileUsingVueJs/blob/master/main.py

## PDF TEXT EXTRACTION
	

## ELASTICSEARCH SUPPORT
	- INDICES - WRITE SCRIPT TO CREATE INDICES
		* USERS
		* CANDIDATES
		* ORGANIZATIONS
	- SQS WRITE / UPDATE / DELETE - TIE TO DYNAMODB CLASSES - LAMBDA OR SERVER CRON ?
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search