"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Copyright 2024 Silver Wolf Technology
"""

import requests
import pathlib
import base64
import sys
import msal
from st2common.runners.base_action import Action


class SendMsMail(Action):
    def __init__(self, config):
        super(SendMsMail, self).__init__(config)
        self.config = config["msmail"]
        self.tenant_id = self.config["tenant_id"]
        self.client_id = self.config["client_id"]
        self.client_secret = self.config["client_secret"]
        self.from_email = self.config["from_email"]

        # MSAL ConfidentialClientApplication for token acquisition
        self._app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret
        )

        self.token = self.get_token()

    def get_token(self):
        scope = ["https://graph.microsoft.com/.default"]
        result = self._app.acquire_token_for_client(scopes=scope)
        if "access_token" in result:
            self.logger.info("Successfully obtained token")
            return result["access_token"]
        else:
            self.logger.error(f"Failed to obtain token: {result.get('error_description', 'Unknown error')}")
            sys.exit(1)


    def run(self, **parameters):
        to_list = parameters["to"]
        cc_list = parameters["cc"]
        attachments = parameters["attachments"]

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }


        try:
            # Creates the email object
            email = {
                "message": {
                    "subject": parameters["subject"],
                    "body": {
                        "contentType": parameters["mime_type"],
                        "content": parameters["body"]
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": recipient
                            }
                        } for recipient in to_list
                    ],
                    "ccRecipients": [
                        {
                            "emailAddress": {
                                "address": cc
                            }
                        } for cc in (cc_list if cc_list else [])
                    ],
                    "from": {
                        "emailAddress": {
                            "address": self.from_email
                        }
                    },
                    "attachments": []
                },
                "saveToSentItems": parameters["save_to_sent_items"]
            }

            # Attach files
            if attachments:
                for attachment_path in attachments:
                    attachment_path = pathlib.Path(attachment_path)
                    if attachment_path.exists():
                        with open(attachment_path, 'rb') as attachment_file:
                            attachment_data = attachment_file.read()
                            attachment_base64 = base64.b64encode(attachment_data).decode()
                            attachment = {
                                "@odata.type": "#microsoft.graph.fileAttachment",
                                "name": attachment_path.name,
                                "contentBytes": attachment_base64,
                                "isInline": False,
                                "contentType": "application/octet-stream"
                            }
                            email["message"]["attachments"].append(attachment)
                    else:
                        self.logger.error(f"Attachment file not found: {attachment_path}")
                        sys.exit(1)
    

            # Send the message as the send from user
            response = requests.post(
                f"https://graph.microsoft.com/v1.0/users/{self.from_email}/sendMail",
                headers=headers,
                json=email
            )

            response.raise_for_status()

            if response.status_code == 202:
                self.logger.info(f"Message sent to {to_list}")
            else:
                self.logger.error(f"Unexpected response code: {response.status_code}")
                sys.exit(1)
        except (requests.exceptions.HTTPError, 
                requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout, 
                requests.exceptions.RequestException) as req_err:
            self.logger.error(f"Request error occurred: {req_err}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Failed to process recipient {to_list}: {e}")
            sys.exit(1)
        return True

