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

from st2common.runners.base_action import Action
import sys
import msal

class BaseAction(Action):
    def __init__(self, config):
        super(BaseAction, self).__init__(config)
        # Required for OAUTH Authentication
        self._tenant_id = self.config["tenant_id"]
        self._client_id = self.config["client_id"]
        self._client_secret = self.config["client_secret"]
        self.from_email = self.config["from_email"]


        # MSAL ConfidentialClientApplication for token acquisition
        self._app = msal.ConfidentialClientApplication(
            self._client_id,
            authority=f"https://login.microsoftonline.com/{self._tenant_id}",
            client_credential=self._client_secret
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



