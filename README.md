# StackStorm Mercury

StackStorm Mercury is a collection of StackStorm actions, workflows, and rules intended to glue together other actions in packs listed on StackStorm Exchange. Of note, it provides a new email action that uses the MS Graph API with OAUTH authentication. It also provides an orquesta workflow that emails a device syslog report and a trigger that sends an email alert when a Nagios service state change is detected.

## Repository Structure

The repository consists of the following components:

- **`actions/`**: This directory contains specific actions implemented using the st2 base action class.
  - `send_msmail`: Uses the MS Graph API to send an email using OAUTH authentication.
  - `send_gmail`: Uses the Google APIs to send an email using OAUTH authentication.
  - `save_data_to_disk.py`: Saves text (CSV), list or dictionary to disk. Useful when saving logs to a temp directory, then attaching the log file to an email. The directory must exist and be writeable by user st2.

  
- **`README.md`**: This file provides an overview of the repository and its contents.

- **`LICENSE`**: This repository is licensed under the Apache-2 terms.

## Getting Started

To install the pack, install the prerequisites then follow this step:

1. Install the pack and required dependencies:

    `st2 pack install https://github.com/fegrimaldi/stackstorm-mercury.git`

2. Use the provided actions or extend them to suit your specific use case.

## Contributing

Contributions to Silverwolf Networks are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

---

Copyright 2024 Silver Wolf Technology - Developed by Fabricio Grimaldi.
