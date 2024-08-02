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

   Copyright 2024 Silver Wolf Technoglogy
"""

import requests
import pathlib
import base64
import sys
from lib import action


class SendEmail(action.BaseAction):
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

