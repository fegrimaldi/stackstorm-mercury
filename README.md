# StackStorm Mercury

StackStorm Mercury is a collection of StackStorm actions, workflows, and rules intended to glue together other actions in packs listed on StackStorm Exchange. Of note, it provides a new email action that uses the MS Graph API with OAUTH authentication. It also provides an orquesta workflow that emails a device syslog report and a trigger that sends an email alert when a Nagios service state change is detected.

## Repository Structure

The repository consists of the following components:

- **`actions/`**: This directory contains specific actions implemented using the st2 base action class.
  - `send_email`: Uses the MS Graph API to send an email using OAUTH authentication.
  - `send_gmail`: Uses the Google APIs to send an email using OAUTH authentication.
  - `save_data_to_disk.py`: Saves text (CSV), list or dictionary to disk. Useful when saving logs to a temp directory, then attaching the log file to an email. The directory must exist and be writeable by user st2.

- **`actions/workflows`**: Workflows
  - `email_syslog_report`: Runs a device syslog query (mysql), formats results to csv, saves it to disk, then emails the report as an attachment. As is, requires the use of a MySQL server Syslog database (rsyslog, rsyslog-mysql). Usually uses Adiscon LogAnalyzer as a web front end. Requires the mysql and csv pack. Orchestrates the following actions:
    - `mysql.select`
    - `csv.format`
    - `mercury.save_data_to_disk`
    - `mercury.send_email`

- **`rules`**: Rules (triggers)
  - `nagios_email_alert`: Sends an alert email in response to a Nagios service state change.
  
- **`README.md`**: This file provides an overview of the repository and its contents.

- **`LICENSE`**: This repository is licensed under the Apache-2 terms.

## Prerequisites

This pack requires the following StackStorm Packs for full functionality. Note that these packs may requiring installing packages at the OS layer. Suggest you read the docs on GitHub before installing.

1. [Nagios](https://github.com/StackStorm-Exchange/stackstorm-nagios)
2. [MySQL](https://github.com/StackStorm-Exchange/stackstorm-mysql)
    1. If you are developing in an st2-docker container, this pack will fail to install until you install the following packages in both the st2client and st2actionrunner containers first. 

        ``sudo apt install pkg-config libmysqlclient-dev build-essential``
    
3. [CSV](https://github.com/StackStorm-Exchange/stackstorm-csv)

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
