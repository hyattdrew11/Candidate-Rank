#!
# 
import os
import mimetypes
import boto3
import uuid
import datetime
from flask import current_app
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re
import s3fs
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from flask import Flask, Blueprint, jsonify, request, json, send_from_directory, jsonify, make_response, render_template
from flask import current_app as app

# GLOBAL VARIABLES
fs 						= s3fs.S3FileSystem(anon=False)
basedir 				= os.path.abspath(os.path.dirname(__file__))
SENDER = 'info@candidaterank.io' 
client = boto3.client('ses', region_name='us-east-1')
CONFIGURATION_SET = "ConfigSet"
CHARSET = "utf-8"

class EmailController:

	def __init__(self):
		print("EMAIL CONTROLLER")
		print(client)
		self.email_header = ''' 
		<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0;" />
        <meta name="format-detection" content="telephone=no" />
        <style>
            body {
                 {
                    margin: 0;
                    padding: 0;
                    min-width: 100%;
                    width: 100% !important;
                    height: 100% !important;
                }
            }
            body,
            table,
            td,
            div,
            p,
            a {
                 {
                    -webkit-font-smoothing: antialiased;
                    text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                    -webkit-text-size-adjust: 100%;
                    line-height: 100%;
                }
            }
            table,
            td {
                 {
                    mso-table-lspace: 0pt;
                    mso-table-rspace: 0pt;
                    border-collapse: collapse !important;
                    border-spacing: 0;
                }
            }
            img {
                 {
                    border: 0;
                    line-height: 100%;
                    outline: none;
                    text-decoration: none;
                    -ms-interpolation-mode: bicubic;
                }
            }
            #outlook a {
                 {
                    padding: 0;
                }
            }
            .ReadMsgBody {
                 {
                    width: 100%;
                }
            }
            .ExternalClass {
                 {
                    width: 100%;
                }
            }
            .ExternalClass,
            .ExternalClass p,
            .ExternalClass span,
            .ExternalClass font,
            .ExternalClass td,
            .ExternalClass div {
                 {
                    line-height: 100%;
                }
            }
            @media all and (min-width: 560px) {
                 {
                    .container {
                         {
                            border-radius: 8px;
                            -webkit-border-radius: 8px;
                            -moz-border-radius: 8px;
                            -khtml-border-radius: 8px;
                        }
                    }
                }
            }
            a,
            a:hover {
                 {
                    color: #127db3;
                }
            }
            .footer a,
            .footer a:hover {
                 {
                    color: #999999;
                }
            }
        </style>
        <title>Candidate Rank</title>
    </head>
    <body
        topmargin="0"
        rightmargin="0"
        bottommargin="0"
        leftmargin="0"
        marginwidth="0"
        marginheight="0"
        width="100%"
        style="
            border-collapse: collapse;
            border-spacing: 0;
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            -webkit-font-smoothing: antialiased;
            text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
            line-height: 100%;
            background-color: #f0f0f0;
            color: #000000;
        "
        bgcolor="#F0F0F0"
        text="#000000"
    >
        <table width="100%" align="center" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse; border-spacing: 0; margin: 0; padding: 0; width: 100%;" class="background">
            <tr>
                <td align="center" valign="top" style="border-collapse: collapse; border-spacing: 0; margin: 0; padding: 0;" bgcolor="#F0F0F0">
                    <table border="0" cellpadding="0" cellspacing="0" align="center" width="560" style="border-collapse: collapse; border-spacing: 0; padding: 0; width: inherit; max-width: 560px;" class="wrapper">
                        <tr>
                            <td align="center" valign="top" style="border-collapse: collapse; border-spacing: 0; margin: 0; padding: 0; padding-left: 6.25%; padding-right: 6.25%; width: 87.5%; padding-top: 20px; padding-bottom: 20px;"></td>
                        </tr>
                    </table>
                    <table border="0" cellpadding="0" cellspacing="0" align="center" bgcolor="#FFFFFF" width="560" style="border-collapse: collapse; border-spacing: 0; padding: 0; width: inherit; max-width: 560px;" class="container">
                        <tr>
                            <td
                                align="left"
                                valign="top"
                                style="
                                    border-collapse: collapse;
                                    border-spacing: 0;
                                    margin: 0;
                                    padding: 0;
                                    padding-left: 6.25%;
                                    padding-right: 6.25%;
                                    width: 87.5%;
                                    font-size: 17px;
                                    font-weight: 400;
                                    line-height: 160%;
                                    padding-top: 25px;
                                    color: #000000;
                                    font-family: sans-serif;
                                "
                                class="paragraph"
                            >
		'''
		self.email_footer = '</td></tr><tr><td align="center" valign="top" style="border-collapse: collapse; border-spacing: 0; margin: 0; padding: 0; padding-left: 6.25%; padding-right: 6.25%; width: 87.5%;padding-top: 25px;" class="line"><hrcolor="#E0E0E0" align="center" width="100%" size="1" noshade style="margin: 0; padding: 0;"/></td></tr><tr><td align="center" valign="top" style="border-collapse: collapse; border-spacing: 0; margin: 0; padding: 0; padding-left: 6.25%; padding-right: 6.25%; width: 87.5%; font-size: 17px; font-weight: 400; line-height: 160%;padding-top: 20px;padding-bottom: 25px;color: #000000;font-family: sans-serif;" class="paragraph">Have a&nbsp;question? <a href="mailto:support@ourteam.com" target="_blank" style="color: #127DB3; font-family: sans-serif; font-size: 17px; font-weight: 400; line-height: 160%;">info@candidate-rank.com</a></td></tr></table></td></tr></table></body></html>'
        # self.table_users = dynamodb.Table(USERS_TABLE)
        # self.table_organizations = dynamodb.Table(ORGANIZATIONS_TABLE)
	def sendTest(self, attachments, address, header, body, subject):
		try:
			with app.app_context():
				mail = Mail(app)

			tmpFiles = []
			# Create a multipart/mixed parent container.
			msg = MIMEMultipart('mixed')
			msg['Subject'] = subject 
			msg['From'] = SENDER
			msg['To'] = address
			# Create a multipart/alternative child container.
			msg_body = MIMEMultipart('alternative')
			# Encode the text and HTML content and set the character encoding. This step is
			# necessary if you're sending a message with characters outside the ASCII range.
			content  = header+body
			print(content)
			plainTxt = re.sub('<[^<]+?>', '', content)
			textpart = MIMEText(plainTxt.encode(CHARSET), 'plain', CHARSET)
			htmlpart = MIMEText(content.encode(CHARSET), 'html', CHARSET)
			# Add the text and HTML parts to the child container.
			msg_body.attach(textpart)
			msg_body.attach(htmlpart)
			response = Message(
				recipients=[address],
				sender=('Candidate Rank', 'info@candidate-rank.com'),
				reply_to='info@candidate-rank.com',
				subject=subject,
			)
			if len(attachments) > 0:
				for x in attachments:
					ATTACHMENT = current_app.config['UPLOAD_DIR'] + '/'+ x['name']
					fs.get(x['path'], ATTACHMENT)
					attcMime = mimetypes.MimeTypes().guess_type(ATTACHMENT)[0]
					with current_app.open_resource(ATTACHMENT) as fp:
						response.attach(os.path.basename(ATTACHMENT), attcMime, fp.read())
			else:
				print("NO ATTACHMENTS")

			response.html = self.email_header + content + self.email_footer
			mail.send(response)
			print("EMAIL SENT")

			for x in tmpFiles:
				os.remove(x)

			return response

		except ClientError as e:
			print(e.response['Error']['Message'])
			return False


	def inviteCandidate(self, attachments, address, header, body, subject):
		try:
			with app.app_context():
				mail = Mail(app)
			tmpFiles = []
			# Create a multipart/mixed parent container.
			msg = MIMEMultipart('mixed')
			msg['Subject'] = subject 
			msg['From'] = SENDER
			msg['To'] = address
			# Create a multipart/alternative child container.
			msg_body = MIMEMultipart('alternative')
			content  = header+body
			plainTxt = re.sub('<[^<]+?>', '', content)
			textpart = MIMEText(plainTxt.encode(CHARSET), 'plain', CHARSET)
			htmlpart = MIMEText(content.encode(CHARSET), 'html', CHARSET)
			# Add the text and HTML parts to the child container.
			msg_body.attach(textpart)
			msg_body.attach(htmlpart)
			response = Message(
				recipients=[address],
				sender=('Candidate Rank', 'info@candidate-rank.com'),
				reply_to='support@candidate-rank.com',
				subject=subject,
			)
			if len(attachments) > 0:
				for x in attachments:
					ATTACHMENT = current_app.config['UPLOAD_DIR'] + '/'+ x['name']
					fs.get(x['path'], ATTACHMENT)	
					ATTACHMENT = current_app.config['UPLOAD_DIR'] + '/'+ x['name']
					fs.get(x['path'], ATTACHMENT)
					attcMime = mimetypes.MimeTypes().guess_type(ATTACHMENT)[0]
					with current_app.open_resource(ATTACHMENT) as fp:
						response.attach(os.path.basename(ATTACHMENT), attcMime, fp.read())
					# # Define the attachment part and encode it using MIMEApplication.
					# att = MIMEApplication(open(ATTACHMENT, 'rb').read())
					# # Add a header to tell the email client to treat this part as an attachment,
					# # and to give the attachment a name.
					# att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
					# # Attach the multipart/alternative child container to the multipart/mixed
					# # parent container.
					# msg.attach(msg_body)
					# # Add the attachment to the parent container.
					# msg.attach(att)
					# # APPEND TMP FILE TO ARRAY FOR DELETION
					# tmpFiles.append(ATTACHMENT)
			else:
				# msg.attach(msg_body)
				print("NO ATTACHMENTS")
				print(msg_body)

			response.html = response.html = self.email_header + content + self.email_footer
			mail.send(response)
			print(response)
			
			for x in tmpFiles:
				os.remove(x)

			return response
		# 
		except ClientError as e:
			print(e.response['Error']['Message'])
			return False

	def confirmCandidate(self, day, address, org):
		try:
			with app.app_context():
				mail = Mail(app)
			print("•••••••••••••••••••••••••••••••••••••••")
			print("•••••••••••••••••••••••••••••••••••••••")
			print(address)
			print("•••••••••••••••••••••••••••••••••••••••")
			print("•••••••••••••••••••••••••••••••••••••••")
			# Create a multipart/mixed parent container.
			content   = "<h5>Your interview date with " +org['name'].upper()+ " has been set.</h5>"
			content  += "<h6>All finalized interview times conform to Central Standard Time.</h6>"
			content  += "<a href='https://candidaterank.io/applicant'>View My Schedule</a>"			
			content  += "<p>If your administrator has set up a virtual waiting room this will become available 24-48 hours prior to your interview date and can be viewed in your schedule. If you have a conflict in your schedule or need help, please contact " +org['admin']+"</p>"
			content  += "<ul><li>Make sure you only have one virtual meeting open at a time</li><li>Refresh your CandidateRank Schedule prior to interviews</li><li>Make sure you have a stable internet connection</li><li>Check all your “Start Zoom” buttons to make sure they have a pointer finger over them</li></ul>"
			
			response = Message(
				recipients=[address],
				sender=('Candidate Rank', 'info@candidate-rank.com'),
				reply_to='support@candidate-rank.com',
				subject=org['name'].upper() + " Interview Date Finalzed",
			)
			response.html = response.html = self.email_header + content + self.email_footer
			mail.send(response)
			return response

		except ClientError as e:
			print(e.response['Error']['Message'])
			return False

	def passwordReset(self, address, link):
		with app.app_context():
			mail = Mail(app)
		print("SEND PASSWORD RESET EMAIL")
		print(address)
		print(link)
		try:
			body =  """<html>
					<head></head>
					<body>
					  <h5>Candidate Rank Password Reset</h5>
					  <p>You have requested a password reset for your candidatew rank account. Click the link below to reset your password.</p>
					"""
			body += link
			body += """
					</body>
					</html>            
					"""
			plainTxt = re.sub('<[^<]+?>', '', body)
			# response = client.send_email(
	  #   		Destination={
	  #       		'ToAddresses': [address],
	  #   		},
	  #   		Message={
	  #       	'Body': {
	  #           	'Html': {
	  #               	'Charset': 'UTF-8',
	  #               	'Data': body,
	  #           	},
	  #           	'Text': {
	  #               	'Charset': 'UTF-8',
	  #               	'Data': plainTxt,
	  #           	},
	  #       	},
	  #       	'Subject': {
	  #           	'Charset': 'UTF-8',
	  #           	'Data': "Candidate Rank Password Reset",
	  #       	},
	  #   	},
	  #   	Source='info@candidaterank.io',
			# )
			response = Message(
				recipients=[address],
				sender=('Candidate Rank', 'info@candidate-rank.com'),
				reply_to='support@candidate-rank.com',
				subject='Candidate Rank Password Reset',
			)
			response.html = response.html = self.email_header + body + self.email_footer
			mail.send(response)
			print(response)
			return response

		except ClientError as e:
			print(e.response['Error']['Message'])
			return False

	def evaluatorInvite(self, address, link, password):
		with app.app_context():
			mail = Mail(app)
		print("SEND PASSWORD RESET EMAIL")
		print(address)
		print(link)
		try:
			body =  """
					  <h2>Welcome to Candidate Rank</h2>
					  <p>Your department administrator has invited you to join this interview season. Use the password provided below to login at <a href="https://candidaterank.io/login">https://candidaterank.io/login</a></p>
					"""
			body += "<h3><strong>"
			body += password
			body += "</strong></h2>"

			plainTxt = re.sub('<[^<]+?>', '', body)
			response = Message(
				recipients=[address],
				sender=('Candidate Rank', 'info@candidate-rank.com'),
				reply_to='support@candidate-rank.com',
				subject='Welcome to Candidate Rank',
			)
			response.html = response.html = self.email_header + body + self.email_footer
			mail.send(response)
			print(response)
			return response

		except ClientError as e:
			print(e.response['Error']['Message'])
			return False