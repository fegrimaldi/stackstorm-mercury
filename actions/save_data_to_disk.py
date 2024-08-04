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

# import os
import json
from st2common.runners.base_action import Action
import sys

class SaveDataToDisk(Action):
    def run(self, **parameters):
        file_path = parameters["file_path"]
        data = parameters["data"]

        try:
            # ? Ensure the directory exists
            #os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Process data based on its type
            if isinstance(data, str):
                # Try to detect if the string is a JSON object
                try:
                    json_data = json.loads(data)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=4)
                    self.logger.info(f"JSON data (from string) saved to {file_path}")
                except json.JSONDecodeError:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(data)
                    self.logger.info(f"Text (CSV) data saved to {file_path}")
            elif isinstance(data, (dict, list)):
                # Save dictionary or list as JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                self.logger.info(f"JSON data saved to {file_path}")
            else:
                raise ValueError("Data must be a string, dictionary, or list.")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to save data payload: {str(e)}")
            sys.exit(1)


