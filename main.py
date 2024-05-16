import os
import base64
import email

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from time import sleep

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
	service = gmail_authentication()
	last_history_id = get_latest_history_id(service)
	while True:
		print(last_history_id)
		sleep(10)
		new_messages = get_new_messages(service,last_history_id)
		if new_messages:
			print(f"Found {len(new_messages)} new messages")
			for message in new_messages:
				message_id = message['message']['id']
				get_message(service, message_id)
				#get_messages_body(service, message_id)
			last_history_id = get_latest_history_id(service)
		else:
			print("No New Message")

# Handle the GMAIL authentication
def gmail_authentication():
	creds = None

	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	# If none's found, let the user log in
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				"credentials.json", SCOPES
			)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open("token.json", "w") as token:
			token.write(creds.to_json())
	# Return service
	return build("gmail", "v1", credentials=creds)

def get_latest_history_id(service):
	response = service.users().getProfile(userId='me').execute()
	return response.get('historyId')

def get_new_messages(service,history_id):
	response = service.users().history().list(
		userId='me',
		startHistoryId=history_id,
		historyTypes=['messageAdded']
	).execute()

	if 'history' in response:
		messages = []
		for history in response['history']:
			for message in history['messagesAdded']:
				messages.append(message)
		return messages
	return []

def get_body(mime_msg):
	if mime_msg.is_multipart():
		for part in mime_msg.walk():
			content_type = part.get_content_type()
			content_disposition = str(part.get("Content-Disposition"))

			if "attachment" not in content_disposition:
				if content_type == "text/plain":
					return part.get_payload(decode=True).decode()
				elif content_type == "text/html":
					return part.get_payload(decode=True).decode()
	else:
		return mime_msg.get_payload(decode=True).decode()
	return ""

def get_message(service, message_id):
	message = service.users().messages().get(
		userId='me',
		id=message_id,
		format='raw'
	).execute()
	mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(message['raw']))
	
	msg_from = mime_msg['from']
	msg_to = mime_msg['to']
	msg_subject = mime_msg['subject']
	msg_body = get_body(mime_msg)

	print(f'From: {msg_from}')
	print(f'To: {msg_to}')
	print(f'Subject: {msg_subject}')
	print("--------------------------------------")
	print(msg_body,end='\n\n')
	print("--------------------------------------")

if __name__ == "__main__":
	main()
