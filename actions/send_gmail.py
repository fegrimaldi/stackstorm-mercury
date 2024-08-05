import os
import sys
import base64
import mimetypes
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from st2common.runners.base_action import Action

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class SendGmail(Action):
    def __init__(self, config):
        super(SendGmail, self).__init__(config)
        self.config = config["gmail"]
        self.creds = None
        self.get_credentials()

    def get_credentials(self):
        """Gets valid user credentials from the StackStorm configuration."""
        client_id = self.config['client_id']
        client_secret = self.config['client_secret']
        refresh_token = self.config['refresh_token']

        self.creds = Credentials(
            None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri='https://oauth2.googleapis.com/token'
        )


        # Refresh the token if it has expired, which it has
        if self.creds and not self.creds.expiry and self.creds._refresh_token:
            try:
                self.creds.refresh(Request())
                self.logger.info(f"New Access Token issued.")
            except Exception as e:
                self.loggger.error(f"Error refreshing token: {e}")



    def create_message(self, to, cc, subject, body, mime_type, attachments):
        """Create a message for an email with optional attachments."""
        message = MIMEMultipart()
        message['to'] = ', '.join(to)  # Join the list into a comma-separated string
        if cc:
            message['cc'] = ', '.join(cc)  # Join the list into a comma-separated string
        message['subject'] = subject

        msg = MIMEText(body, mime_type)
        message.attach(msg)

        if attachments:
            for file_path in attachments:
                content_type, encoding = mimetypes.guess_type(file_path)
                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'
                main_type, sub_type = content_type.split('/', 1)

                with open(file_path, 'rb') as f:
                    file_msg = MIMEBase(main_type, sub_type)
                    file_msg.set_payload(f.read())
                    encoders.encode_base64(file_msg)

                filename = os.path.basename(file_path)
                file_msg.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(file_msg)

        raw_message = base64.urlsafe_b64encode(message.as_string().encode()).decode()
        return {'raw': raw_message}

    def send_message(self, user_id, message):
        """Send an email message using the Gmail API."""
        try:
            headers = {'Authorization': f'Bearer {self.creds.token}'}
            response = requests.post(
                f'https://www.googleapis.com/gmail/v1/users/{user_id}/messages/send',
                headers=headers,
                json=message
            )
            response.raise_for_status()
            self.logger.info(f'Sent! Message Id: {response.json().get("id")}')
            return response.json()
        except (requests.exceptions.HTTPError, 
                requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout, 
                requests.exceptions.RequestException) as error:
            self.logger.error(f'An error occurred: {error}')
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"General error occurred: {e}")
            sys.exit(1)

    def run(self, **parameters):
        to = parameters.get('to')
        cc = parameters.get('cc', [])
        subject = parameters.get('subject')
        body = parameters.get('body')
        mime_type = parameters.get('mime_type', 'plain')
        attachments = parameters.get('attachments', [])

        message = self.create_message(to, cc, subject, body, mime_type, attachments)
        result = self.send_message("me", message)
        return result

